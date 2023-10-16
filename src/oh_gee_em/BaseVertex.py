from __future__ import annotations

from typing import Union

from pydantic import BaseModel, computed_field
from pydantic.functional_validators import Annotated, AfterValidator
from gremlin_python.process.traversal import Cardinality, T, Merge
from uuid import UUID
import logging

logger = logging.getLogger(__name__)

def enum_UUID_to_str(value):
    if isinstance(value, T):
        return value.name
    if isinstance(value, UUID):
        return str(value)
    return value

def _ftv(property_map: dict) -> dict:
    """Take a tinker vertex that has <T.id:...>: some-identifier enums as keys and convert them
    to strings so they're useable with **kwargs / sane user values.

    Args:
        property_map (dict): The map that needs to be converted to a "sane" representation without T.id and T.label keys

    Returns:
        dict: The cleaned up property_map
    """
    if property_map is None:
        raise Exception("'None' is not of type 'dict'")

    property_map[T.id.name] = str(property_map.pop(T.id, None))
    property_map[T.label.name] = property_map.pop(T.label, None)
    return property_map
    
class BaseVertex(BaseModel):
    id: Annotated[Union[str, T, UUID], AfterValidator(enum_UUID_to_str)] = None

    def __del__(self):
        logger.warning("This will not delete the record in the database, only the local instance!")

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
    def create_vertex(cls, g, *args, **kwargs) -> BaseVertex:
        vertex = next(g.merge_v(kwargs).element_map(), None)
        if not vertex:
            # raise here instead? creation had to have failed.
            return None
        
        vertex = _ftv(vertex)
        return cls(**vertex)

    @classmethod
    def get_or_create_vertex(cls, g, *args, id: str | int = None, **kwargs) -> BaseVertex:
        id_map = {}
        if id:
            id_map = {T.id: id}

        vertex = next(g.merge_v(id_map).option(Merge.on_create, kwargs).element_map(), None)
        if not vertex:
            return None
        
        vertex = _ftv(vertex)
        return cls(**vertex)

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

        vertex = next(g.merge_v(id_map).option(Merge.on_match, self.model_dump(exclude_none=True)).element_map(), None)
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

        vertex = next(g.merge_v(id_map).option(Merge.on_create, self.model_dump(exclude_none=True)).element_map(), None)
        if not vertex:
            # raise here instead? creation had to have failed.
            return None

        vertex = _ftv(vertex)
        self.update(**vertex)
        return self

    def delete(self, g) -> None:
        g.V(self.id).drop().iterate()