from uuid import uuid4

from oh_gee_em import BaseVertex


# ---------------------------------------------------------------------------- #
#                              @CLASS METHOD TESTS                             #
# ---------------------------------------------------------------------------- #
def test_base_create_no_id(g, reset) -> None:
    base = BaseVertex.create_vertex(g)
    assert base.id is not None
    assert base.label == "basevertex"


def test_base_create_provided_id(g, reset) -> None:
    test_id = str(uuid4())
    base = BaseVertex.create_vertex(g, id=test_id)
    assert base.id == test_id
    assert base.label == "basevertex"


# TODO: add int id tests


def test_base_goc_no_id(g, reset) -> None:
    base = BaseVertex.get_or_create_vertex(g)
    assert base.id is not None
    assert base.label == "basevertex"


def test_base_goc_provided_id(g, reset) -> None:
    test_id = str(uuid4())
    base = BaseVertex.get_or_create_vertex(g, id=test_id)
    assert base.id == test_id
    assert base.label == "basevertex"
