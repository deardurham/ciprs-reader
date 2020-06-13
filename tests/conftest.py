import pytest

from ciprs_reader.parser.state import ParserState


@pytest.fixture
def report():
    return {}


@pytest.fixture
def state():
    return ParserState()
