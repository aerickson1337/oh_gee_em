from uuid import uuid4

from gremlin_python.process.traversal import T

from oh_gee_em.utilities import enum_uuid_to_str


def test_enum_str_util_uuid() -> None:
    test_uuid = uuid4()
    str_uuid = enum_uuid_to_str(test_uuid)
    assert str_uuid == str(test_uuid)
    assert isinstance(str_uuid, str)


def test_enum_str_util_T():
    str_id = enum_uuid_to_str(T.id)
    assert str_id == T.id.name
    assert isinstance(str_id, str)

    str_label = enum_uuid_to_str(T.label)
    assert str_label == T.label.name
    assert isinstance(str_label, str)
