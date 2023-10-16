"""Test cases for the __main__ module."""
import pytest

from uuid import uuid4
from gremlin_python.process.anonymous_traversal import traversal
from gremlin_python.process.graph_traversal import __
from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection
from gremlin_python.process.traversal import Cardinality, T, Merge
from gremlin_python.process.graph_traversal import GraphTraversalSource

from oh_gee_em import BaseVertex, __main__

class Person(BaseVertex):
    name: str
    age: int
    sex: str

@pytest.fixture(scope='session')
def g() -> GraphTraversalSource:
    """Fixture for invoking command-line interfaces."""
    url = 'ws://localhost:8182/gremlin'
    remoteConn = DriverRemoteConnection(url, 'g')

    g = traversal().with_remote(remoteConn)
    yield g
    remoteConn.close()

@pytest.fixture(scope="function")
def reset(g) -> None:
    g.V().drop().iterate()

# ---------------------------------------------------------------------------- #
#                              @CLASS METHOD TESTS                             #
# ---------------------------------------------------------------------------- #
def test_mock_person_create_vertex(g, reset) -> None:
    fred = Person.create_vertex(g, name="fred", age=22, sex="m")
    assert fred.name == "fred"
    assert fred.age == 22
    assert fred.sex == "m"

def test_mock_person_get_vertex_dne(g, reset) -> None:
    fred = Person.get_vertex(g, id=str(uuid4()))
    assert fred == None

def test_mock_person_get_or_create_vertex_1(g, reset) -> None:
    """test just the creation part of get or create
    """
    fred = Person.get_or_create_vertex(g, name="fred", age=22, sex="m")
    assert fred.name == "fred"
    assert fred.age == 22
    assert fred.sex == "m"
    assert fred.label == fred.__class__.__name__.lower()

def test_mock_person_get_or_create_vertex_2(g, reset) -> None:
    """test creating and then getting fred
    """
    # create fred
    fred1 = Person.create_vertex(g, name="fred", age=22, sex="m")
    assert fred1.name == "fred"
    assert fred1.age == 22
    assert fred1.sex == "m"

    # get fred
    fred2 = Person.get_vertex(g, id=fred1.id)
    assert fred2.name == "fred"
    assert fred2.age == 22
    assert fred2.sex == "m"

def test_mock_person_get_or_create_vertex_2(g, reset) -> None:
    """test creating and then getting fred
    """
    # create fred
    fred1 = Person.create_vertex(g, name="fred", age=22, sex="m")
    assert fred1.name == "fred"
    assert fred1.age == 22
    assert fred1.sex == "m"

    # get fred
    fred2 = Person.get_vertex(g, id=fred1.id)
    assert fred2.name == "fred"
    assert fred2.age == 22
    assert fred2.sex == "m"

# ---------------------------------------------------------------------------- #
#                          REGULAR CLASS METHOD TESTS                          #
# ---------------------------------------------------------------------------- #
def test_mock_person_save_1(g, reset) -> None:
    """test creating and then getting fred
    """
    # create fred
    person = Person.create_vertex(g, name="fred", age=22, sex="m")
    # update their information
    person.name = "frederick"
    person.age = 23
    # save to graph
    person.save(g)

    # validate update is correct locally
    assert person.name == "frederick"
    assert person.age == 23
    assert person.sex == "m"

    # validate update is correct when loaded
    francine = Person.get_vertex(g, id=person.id)
    assert person.name == "frederick"
    assert person.age == 23
    assert person.sex == "m"

def test_mock_person_save_2(g, reset) -> None:
    """test local updates only pushed on .save()
    """
    fred = Person.create_vertex(g, name="fred", age=22, sex="m")
    evil_fred = Person.get_vertex(g, id=fred.id)
    
    fred.name = "frederick"

    evil_fred.name = "evil frederick"
    evil_fred.age = 10000
    evil_fred.sex = "evil"
    evil_fred.save(g)
    assert evil_fred.name == "evil frederick"
    assert evil_fred.age == 10000
    assert evil_fred.sex == "evil"
    assert fred.name == "frederick"

    fred.save(g)
    assert fred.name == "frederick"
    assert fred.age == 22
    assert fred.sex == "m"
    assert evil_fred.name == "evil frederick"
    assert evil_fred.age == 10000
    assert evil_fred.sex == "evil"

def test_mock_person_update(g, reset) -> None:
    """test update(**dict) convenince method works 
    """
    fred = Person.create_vertex(g, name="fred", age=22, sex="m")
    
    fred.update(**{"name":"frederick", "age": 50})
    assert fred.name == "frederick"
    assert fred.age == 50

def test_mock_person_create_no_id(g, reset) -> None:
    """test Person.create() convenince method works with automatic id
    """
    fred = Person(name="fred", age=22, sex="m")
    fred.create(g)

    assert fred.name == "fred"
    assert fred.age == 22
    assert fred.sex == "m"

def test_mock_person_create_id_manually_set(g, reset) -> None:
    """test Person.create() convenince method works with manual id
    """
    test_id = str(uuid4())
    fred = Person(id=test_id, name="fred", age=22, sex="m")
    fred.create(g)

    assert fred.id == test_id
    assert fred.name == "fred"
    assert fred.age == 22
    assert fred.sex == "m"

def test_mock_person_delete(g, reset) -> None:
    """test Person.delete() convenince method works
    """
    fred = Person(name="fred", age=22, sex="m")
    fred.create(g)
    
    assert fred.name == "fred"
    assert fred.age == 22
    assert fred.sex == "m"

    # need to set fred = result so the ref count drops to 0 and this gets collected
    # not sure there's a way in python to hard delete this reference, with an api like
    # Person.delete(g, fred), guessing not.
    fred = Person.delete(g, fred)
    assert fred == None
