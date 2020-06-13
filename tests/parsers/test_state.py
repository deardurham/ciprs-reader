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


@pytest.mark.parametrize("Parser", [lines.OffenseRecordRow])
def test_parser__disabled(Parser, report, state):
    parser = Parser(report, state)
    assert not parser.is_enabled()


def test_case_details__disabled(report, state):
    state.section = "Not Header"
    parser = lines.CaseDetails(report, state)
    assert not parser.is_enabled()


def test_offense_record_row__enabled(report, state):
    state.offense_num = 1
    state.section = Section.DISTRICT_OFFENSE
    assert lines.OffenseRecordRow(report, state).is_enabled()
