import random
import uuid

import names
import pytest

from .test_utilities import People
from .test_utilities import Person

age_range = range(-10, 200)
sex_opts = ["m", "f", None]

@pytest.fixture
def local_people() -> People:
    return People(
        {
            Person(id=uuid.uuid4(), name="fred", age=25, sex="m"),
            Person(id=uuid.uuid4(), name="ron", age=40, sex="m"),
            Person(id=uuid.uuid4(), name="becky", age=27, sex="f"),
        }
    )


@pytest.fixture
def db_people(g, local_people) -> People:
    for person in local_people:
        person.create(g)
    return local_people


def random_person() -> Person:
    return Person(
        id=uuid.uuid4(),
        name=names.get_first_name(),
        age=random.choice(age_range),
        sex=random.choice(sex_opts),
    )


@pytest.fixture
def local_random_people(count) -> Person:
    people_set = set()
    for i in range(0, count):
        people_set.add(random_person())
    return People(people_set)


# ---------------------------------------------------------------------------- #
#                              @CLASS METHOD TESTS                             #
# ---------------------------------------------------------------------------- #
@pytest.mark.parametrize("count", [1, 1000, 5000])
def test_base_vertices_create_x(g, reset, count, local_random_people) -> None:
    local_random_people.create(g)
    assert len(local_random_people) == count

@pytest.mark.parametrize("count", [1])
def test_base_vertices_save_x(g, reset, count, local_random_people) -> None:
    local_random_people.create(g)
    assert len(local_random_people) == count

    for person in local_random_people:
        person.name = "new_bulk_name"
        person.age = 69
    local_random_people.save(g)

    for person in local_random_people:
        assert g.V(person.id).properties("name").value().next() == "new_bulk_name"
        assert g.V(person.id).properties("age").value().next() == 69

@pytest.mark.parametrize("count", [1])
def test_base_vertices_save_None(g, reset, count, local_random_people) -> None:
    local_random_people.create(g)
    assert len(local_random_people) == count

    for person in local_random_people:
        person.name = "new_bulk_name"
        person.age = 69
        person.sex = None
    local_random_people.save(g)
    

    for person in local_random_people:
        assert next(g.V(person.id).properties("name").value(), None) == "new_bulk_name"
        assert next(g.V(person.id).properties("age").value(), None) == 69
        assert next(g.V(person.id).properties("sex").value(), None) is None

@pytest.mark.parametrize("count", [1])
def test_base_vertices_save_drop_x(g, reset, count, local_random_people) -> None:
    local_random_people.create(g)
    assert len(local_random_people) == count

    for person in local_random_people:
        person.name = "new_bulk_name"
        person.age = 69
        # TODO: see if there's a more intuitive way to do this
        # having person.sex = None set the property to None makes sense
        # person.drop(...) also makes sense that it removes the property afaict
        # but being able to just do person."property".drop would be nicer...
        person.drop(g, "sex")
    local_random_people.save(g)

    for person in local_random_people:
        assert next(g.V(person.id).properties("name").value(), None) == "new_bulk_name"
        assert next(g.V(person.id).properties("age").value(), None) == 69
        assert next(g.V(person.id).properties("sex").value(), None) is None
