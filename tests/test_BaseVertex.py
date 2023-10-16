"""Test cases for the __main__ module."""
import pytest

from gremlin_python.process.anonymous_traversal import traversal
from gremlin_python.process.graph_traversal import __
from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection
from gremlin_python.process.traversal import Cardinality, T, Merge

from oh_gee_em import BaseVertex, __main__

class Person(BaseVertex):
    name: str
    age: int
    sex: str

@pytest.fixture(scope='session')
def g():
    """Fixture for invoking command-line interfaces."""
    url = 'ws://localhost:8182/gremlin'
    remoteConn = DriverRemoteConnection(url, 'g')

    g = traversal().with_remote(remoteConn)
    yield g
    remoteConn.close()

@pytest.fixture(scope="function")
def reset(g):
    g.V().drop().iterate()

def test_mock_person_gocv(g, reset) -> None:
    fred = Person.get_or_create_vertex(g, name="fred", age=22, sex="m")
    assert fred.name == "fred"
    assert fred.age == 22
    assert fred.sex == "m"

def test_mock_person(g, reset) -> None:
    fred = Person.get_or_create_vertex(g, name="ted", age=11, sex="f")
    assert fred.name == "ted"
    assert fred.age == 11
    assert fred.sex == "f"

