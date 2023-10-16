from typing import Union

from pydantic import BaseModel, ConfigDict
from pydantic.functional_validators import Annotated, AfterValidator
from gremlin_python.process.traversal import Cardinality, T, Merge
from uuid import UUID

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
    property_map[T.id.name] = property_map.pop(T.id, None)
    property_map[T.label.name] = property_map.pop(T.label, None)
    return property_map
    
class BaseVertex(BaseModel):
    id: Annotated[Union[str, T, UUID], AfterValidator(enum_UUID_to_str)] = None
    label: Annotated[Union[str, T], AfterValidator(enum_UUID_to_str)] = None

    @classmethod
    def get_vertex(cls, g, id: str | int):
        vertex = g.V(id).element_map().next()
        vertex = _ftv(property_map=vertex)
        return cls(**vertex)

    @classmethod
    def create_vertex(cls, g, *args, **kwargs):
        g.merge_v(kwargs).iterate()
        return cls(**kwargs)

    @classmethod
    def get_or_create_vertex(cls, g, *args, id: str | int = None, **kwargs):
        id_map = {}
        if id:
            id_map = {T.id: id}
        vertex = g.merge_v(id_map).option(Merge.on_create, kwargs).element_map().next()
        vertex = _ftv(property_map=vertex)
        return cls(**vertex)

