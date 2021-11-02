import pytest
import random
import string

from name import Name


@pytest.fixture
def name():
    return get_name()


def get_name():
    length = random.randint(1, 12)
    first = "".join(
        random.choices(
            string.ascii_uppercase + string.ascii_lowercase, k=length
        )
    )
    last = "".join(
        random.choices(string.ascii_uppercase + string.digits, k=length)
    )
    return Name(parts=[first, last], sort_order=(0, 1))


@pytest.fixture
def name_factory():
    class NameFactory(object):
        def get(self):
            name_factory = get_name()
            return name_factory

    return NameFactory()


def test_name_equals(name_factory) -> None:
    ret = 0
    # using loop on the small chace that the random names are the same
    for i in range(1, 10):
        name1 = name_factory.get()
        name2 = name_factory.get()
        if name1 != name2:
            ret += 1
    assert ret >= 5


def test_name_sort() -> None:
    name1 = Name(["Bob", "T", "Smith"])
    name2 = Name(["Zee", "Atlantic"], (1, 0))
    name3 = Name(["Zee", "Atlantic"], (0, 1))
    name4 = Name(["Zee", "Atlantic"])
    assert name1 > name2 and str(name1) < str(name2)
    assert name1 < name3
    assert name1 < name4


def test_name_repr() -> None:
    name = Name(["Niomi", "Turle"])
    name2 = eval(repr(name))
    print(name2)
