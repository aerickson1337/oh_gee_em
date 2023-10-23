from __future__ import annotations

import logging
from uuid import UUID
from uuid import uuid4

from gremlin_python.process.traversal import Merge
from gremlin_python.process.traversal import T
from pydantic import BaseModel
from pydantic import Field
from pydantic import computed_field
from pydantic.functional_validators import AfterValidator
from pydantic.functional_validators import Annotated

from .utilities import _ftv
from .utilities import enum_uuid_to_str


logger = logging.getLogger(__name__)  # pragma: no cover


class BaseVertex(BaseModel):
    id: Annotated[str | int | T | UUID, AfterValidator(enum_uuid_to_str)] = Field(
        default=uuid4(),
    )

    def __hash__(self):
        return hash(self.id)

    def tinker_id(self):
        if self.id:
            return {T.id: self.id}
        return {}

    def tinker_id_label(self):
        if self.id:
            return {T.id: self.id, T.label: self.label}
        return {}

    def dump_props(self, add_label=True, exclude=("id", "label"), **kwargs):
        if add_label:
            return {T.label: self.label, **self.model_dump(exclude=exclude, **kwargs)}
        return self.model_dump(exclude=exclude, **kwargs)

    def project(self):
        projection_dict = {}
        projection_dict["id"] = self.id
        projection_dict["label"] = self.label

        return {**projection_dict, **self.model_dump(exclude=["id", "label"])}

    @computed_field
    @property
    def label(self) -> str:
        return self.__class__.__name__.lower()

    @label.setter
    def label(self, value: str) -> None:
        pass

    @classmethod
    def get_vertex(cls, g, id: str | int) -> BaseVertex:
        """Get a vertex from the database from the given "id".

        Args:
            g (GraphTraversalSource): The GraphTraversalSource used to get the vertex.
            id (str | int): The T.id or id of the vertex in the graph.

        Returns:
            BaseVertex: A created instance of the class that called this method.
        """
        vertex = next(g.V(id).element_map(), None)
        if vertex is None:
            return None

        vertex = _ftv(vertex)
        return cls(**vertex)

    @classmethod
    def create_vertex(cls, g, *args, id: str | int = None, **kwargs) -> BaseVertex:
        """Create the vertex at id based on this class."""
        id_map = {}
        if id:
            id_map = {T.id: id}

        vertex = next(
            g.merge_v(id_map).option(Merge.on_create, kwargs).element_map(), None
        )
        if not vertex:
            # raise here instead? creation had to have failed.
            return None

        vertex = _ftv(vertex)
        return cls(**vertex)

    @classmethod
    def get_or_create_vertex(
        cls, g, *args, id: str | int = None, **kwargs
    ) -> BaseVertex:
        """load or create the BaseVertex at the given id."""
        return cls.create_vertex(g, *args, id=id, **kwargs)

    @classmethod
    def delete_vertex(cls, g, BaseVertex) -> None:
        """pass a BaseVertex to this classmethod to delete it from the db."""
        g.V(BaseVertex.id).drop().iterate()

    def update(self, **update_fields) -> BaseVertex:
        """updates this class"""
        for field, value in update_fields.items():
            setattr(self, field, value)
        return self

    def save(self, g) -> BaseVertex:
        """save mutations to current class to db, load what db returned."""
        # on_match doesn't like T.label, skip passing in this context since some graph
        # providers don't let you update label without re-creating the vertex.
        vertex = next(
            g.merge_v(self.tinker_id())
            .option(Merge.on_match, self.dump_props(add_label=False, exclude_none=True))
            .element_map(),
            None,
        )
        if not vertex:
            return None

        # remove the enum keys cause they break python classes
        vertex = _ftv(vertex)

        # multiple people could change these values at the same time,
        # so update the model with what source of truth gave back.
        self.update(**vertex)

        return self

    def create(self, g) -> BaseVertex:
        """create this class in the db if it doesn't exist."""
        vertex = next(
            g.merge_v(self.tinker_id())
            .option(Merge.on_create, self.dump_props(exclude_none=True))
            .element_map(),
            None,
        )
        if not vertex:
            # raise here instead? creation had to have failed.
            return None

        vertex = _ftv(vertex)
        self.update(**vertex)
        return self

    def delete(self, g) -> None:
        """delete this class from the db."""
        g.V(self.id).drop().iterate()


    def drop(self, g, property) -> BaseVertex:
        setattr(self, property, next(g.V(self.id).properties(property).drop(), None))
        return self
