import pytest

from ciprs_reader.parser.offense import Offenses, Offense


@pytest.fixture
def offense():
    return Offense()


@pytest.fixture
def offenses():
    return Offenses()


def test_offenses_starts_empty(offenses):
    assert len(offenses) == 0


def test_offenses_new(offenses):
    offenses.new()
    assert len(offenses) == 1


def test_offenses_current_always_exists(offenses):
    assert offenses.current == {}


def test_add_record(offense):
    record = {"foo": "bar"}
    offense.add_record(record)
    assert offense["Records"][-1] == record
