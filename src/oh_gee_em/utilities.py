"""utilities for converting between the tinkerpop interface and the pydantic one."""
from uuid import UUID

from gremlin_python.process.traversal import T


def enum_uuid_to_str(value: str | UUID | T) -> str | int:
    """Take a given value and make it a string or int.

    Take things that cause issues Neptune/other clouds like the python UUID() object
    or in python classes like gremlins T enum and make it into a string.

    Args:
        value (str | UUID | T): The painful value to convert to a string.

    Returns:
        str | int: Returns a string or int depending on passed in value.
            [UUID, T, str] -> str
            int -> int
    """
    if isinstance(value, T):
        return value.name
    if isinstance(value, UUID):
        return str(value)
    return value


def _ftv(property_map: dict) -> dict:
    """Takes a dictionary and tweaks to be python class friendly.

    Args:
        property_map (dict): The dictionary to tweak,
            generally from a value_map or element_map step.

    Raises:
        Exception: Raised when you pass None into this since you can't pop None.

    Returns:
        dict: The modified property_map which is able to be used in a class
            via ** kwargs.
    """
    if property_map is None:
        raise Exception("'None' is not of type 'dict'")

    property_map[T.id.name] = str(property_map.pop(T.id, None))
    property_map[T.label.name] = property_map.pop(T.label, None)
    return property_map
