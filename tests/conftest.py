import pytest

from ciprs_reader.parser.state import ParserState
from ciprs_reader.parser.offense import Offenses, Offense


@pytest.fixture
def report():
    return {}


@pytest.fixture
def state():
    return ParserState()


@pytest.fixture
def offense():
    return Offense()


@pytest.fixture
def offenses():
    return Offenses()
