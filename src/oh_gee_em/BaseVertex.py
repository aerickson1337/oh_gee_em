from __future__ import annotations

import logging
from typing import Union
from uuid import UUID

from gremlin_python.process.traversal import Cardinality
from gremlin_python.process.traversal import Merge
from gremlin_python.process.traversal import T
from pydantic import BaseModel
from pydantic import computed_field
from pydantic.functional_validators import AfterValidator
from pydantic.functional_validators import Annotated

from .utilities import _ftv
from .utilities import enum_UUID_to_str


logger = logging.getLogger(__name__)  # pragma: no cover


class BaseVertex(BaseModel):
    id: Annotated[str | int | T | UUID, AfterValidator(enum_UUID_to_str)] = None

    def __del__(self):
        logger.warning(
            "This will not delete the record in the database, only the local instance!"
        )

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
        return cls.create_vertex(g, *args, id=id, **kwargs)

    @classmethod
    def delete_vertex(cls, g, BaseVertex) -> None:
        g.V(BaseVertex.id).drop().iterate()

    def update(self, **update_fields) -> BaseVertex:
        for field, value in update_fields.items():
            setattr(self, field, value)
        return self

    def save(self, g) -> BaseVertex:
        id_map = {}
        if self.id:
            id_map = {T.id: str(self.id)}

        vertex = next(
            g.merge_v(id_map)
            .option(Merge.on_match, self.model_dump(exclude_none=True))
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
        id_map = {}
        if self.id:
            id_map = {T.id: str(self.id)}

        vertex = next(
            g.merge_v(id_map)
            .option(Merge.on_create, self.model_dump(exclude_none=True))
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
        g.V(self.id).drop().iterate()
