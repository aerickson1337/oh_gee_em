from uuid import UUID

from gremlin_python.process.traversal import T


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
