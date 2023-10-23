"""Test cases for the __main__ module."""
from uuid import uuid4

import pytest

from oh_gee_em import BaseVertex


class Person(BaseVertex):
    name: str
    age: int
    sex: str | None = None


@pytest.fixture
def fred():
    return Person(id=uuid4(), name="fred", age="22", sex="m")


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
    assert fred is None


def test_mock_person_get_or_create_vertex_1(g, reset) -> None:
    """test just the creation part of get or create"""
    fred = Person.get_or_create_vertex(g, name="fred", age=22, sex="m")
    assert fred.name == "fred"
    assert fred.age == 22
    assert fred.sex == "m"
    assert fred.label == fred.__class__.__name__.lower()


def test_mock_person_get_or_create_vertex_2(g, reset) -> None:
    """test creating and then getting fred"""
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


def test_mock_person_delete_vertex(g, reset) -> None:
    """Test Person.delete() convenince method works."""
    fred = Person.create_vertex(g, name="fred", age=22, sex="m")
    # need to set fred = result so the ref count drops to 0 and this gets collected
    # not sure there's a way in python to hard delete this reference, with an api like
    # del fred, guessing not.
    fred = Person.delete_vertex(g, fred)
    assert fred is None


# ---------------------------------------------------------------------------- #
#                          REGULAR CLASS METHOD TESTS                          #
# ---------------------------------------------------------------------------- #
def test_mock_person_save_1(g, reset, fred) -> None:
    """test creating and then getting fred"""
    # create fred
    fred.create(g)
    # update their information
    fred.name = "frederick"
    fred.age = 23
    # save to graph
    fred.save(g)

    # validate update is correct locally
    assert fred.name == "frederick"
    assert fred.age == 23
    assert fred.sex == "m"

    # validate update is correct when loaded
    Person.get_vertex(g, id=fred.id)
    assert fred.name == "frederick"
    assert fred.age == 23
    assert fred.sex == "m"


def test_mock_person_save_2(g, reset, fred) -> None:
    """test local updates only pushed on .save()"""
    fred.create(g)
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


def test_mock_person_update(g, reset, fred) -> None:
    """test update(**dict) convenince method works"""
    fred.create(g)
    fred.update(**{"name": "frederick", "age": 50})
    assert fred.name == "frederick"
    assert fred.age == 50


def test_mock_person_create_no_id(g, reset, fred) -> None:
    """test Person.create() convenince method works with automatic id"""
    fred.create(g)

    assert fred.name == "fred"
    assert fred.age == 22
    assert fred.sex == "m"


def test_mock_person_create_id_manually_set(g, reset, fred) -> None:
    """test Person.create() convenince method works with manual id"""
    test_id = str(uuid4())
    fred.id = test_id
    fred.create(g)

    assert fred.id == test_id
    assert fred.name == "fred"
    assert fred.age == 22
    assert fred.sex == "m"


def test_mock_person_delete(g, reset, fred) -> None:
    """test Person.delete() convenince method works"""
    fred.create(g)

    assert fred.name == "fred"
    assert fred.age == 22
    assert fred.sex == "m"

    # need to set fred = result so the ref count drops to 0 and this gets collected
    # not sure there's a way in python to hard delete this reference, with an api like
    # del fred, guessing not.
    fred = fred.delete(g)
    assert fred is None


def test_mock_person_drop(g, reset, fred) -> None:
    """test Person.drop() property convenince method works"""
    fred.create(g)

    assert fred.name == "fred"
    assert fred.age == 22
    assert fred.sex == "m"

    fred.drop(g, "name")
    fred.drop(g, "age")
    fred.drop(g, "sex")
    assert fred.name is None
    assert fred.age is None
    assert fred.sex is None
    assert g.V(fred.id).properties("name").values().to_list() == []
    assert g.V(fred.id).properties("age").values().to_list() == []
    assert g.V(fred.id).properties("sex").values().to_list() == []
