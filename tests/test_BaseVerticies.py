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
@pytest.mark.parametrize("count", [1])
def test_base_vertices_create_1(g, reset, count, local_random_people) -> None:
    local_random_people.create(g)
    assert len(local_random_people) == count


@pytest.mark.parametrize("count", [100])
def test_base_vertices_create_2(g, reset, count, local_random_people) -> None:
    local_random_people.create(g)
    assert len(local_random_people) == count


@pytest.mark.parametrize("count", [250])
def test_base_vertices_create_3(g, reset, count, local_random_people) -> None:
    local_random_people.create(g)
    assert len(local_random_people) == count


@pytest.mark.parametrize("count", [500])
def test_base_vertices_create_4(g, reset, count, local_random_people) -> None:
    local_random_people.create(g)
    assert len(local_random_people) == count


@pytest.mark.parametrize("count", [1000])
def test_base_vertices_create_5(g, reset, count, local_random_people) -> None:
    local_random_people.create(g)
    assert len(local_random_people) == count


@pytest.mark.parametrize("count", [5000])
def test_base_vertices_create_5000(g, reset, count, local_random_people) -> None:
    local_random_people.create(g)
    assert len(local_random_people) == count
    assert g.V().has_label("person").count().next() == count
