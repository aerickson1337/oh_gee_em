from uuid import uuid4

import pytest
from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection
from gremlin_python.process.anonymous_traversal import traversal
from gremlin_python.process.graph_traversal import GraphTraversalSource
from gremlin_python.process.graph_traversal import __
from gremlin_python.process.traversal import Cardinality
from gremlin_python.process.traversal import Merge
from gremlin_python.process.traversal import T

from oh_gee_em import BaseVertex


class Person(BaseVertex):
    name: str
    age: int
    sex: str


@pytest.fixture
def fred():
    return Person(name="fred", age="22", sex="m")


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
