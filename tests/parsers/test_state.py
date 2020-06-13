import pytest

from ciprs.const import Section
from ciprs.parser import lines
from ciprs.parser.state import ParserState


@pytest.fixture
def report():
    return {}


@pytest.fixture
def state():
    return ParserState()


def test_offense_record_row__in_state(report, state):
    parser = lines.OffenseRecordRow(report, state)
    assert not parser.in_state()


def test_offense_record_row__not_in_state(report, state):
    state.offense_num = 1
    state.section = Section.DISTRICT_OFFENSE
    assert lines.OffenseRecordRow(report, state).in_state()
