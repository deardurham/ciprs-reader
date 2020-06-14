import pytest

from ciprs_reader.const import Section
from ciprs_reader.parser import lines
from ciprs_reader.parser.section import header, case_information


@pytest.mark.parametrize(
    "Parser",
    [
        case_information.CaseStatus,
        case_information.OffenseDate,
        case_information.OffenseDateTime,
        case_information.CaseWasServedOnDate,
        lines.DefendantRace,
        lines.DefendantSex,
        lines.OffenseRecordRowWithNumber,
        lines.OffenseRecordRow,
    ],
)
def test_parser__disabled_by_default(Parser, report, state):
    parser = Parser(report, state)
    assert not parser.is_enabled()


@pytest.mark.parametrize(
    "Parser", [header.CaseDetails, header.DefendantName,],
)
def test_header_parsers__enabled(Parser, report, state):
    state.section = Section.HEADER
    assert Parser(report, state).is_enabled()


@pytest.mark.parametrize(
    "Parser", [header.CaseDetails, header.DefendantName,],
)
def test_header_parsers__disabled(Parser, report, state):
    state.section = "Not Header"
    assert not Parser(report, state).is_enabled()


@pytest.mark.parametrize(
    "Parser",
    [
        case_information.CaseStatus,
        case_information.OffenseDate,
        case_information.OffenseDateTime,
        case_information.CaseWasServedOnDate,
    ],
)
def test_case_information_parsers__enabled(Parser, report, state):
    state.section = Section.CASE_INFORMATION
    assert Parser(report, state).is_enabled()


@pytest.mark.parametrize(
    "Parser", [lines.DefendantRace, lines.DefendantSex],
)
def test_defendant_parsers__enabled(Parser, report, state):
    state.section = Section.DEFENDANT
    assert Parser(report, state).is_enabled()


@pytest.mark.parametrize(
    "section", [Section.DISTRICT_OFFENSE, Section.SUPERIOR_OFFENSE],
)
def test_offense_record_row_with_number__enabled(section, report, state):
    state.section = section
    assert lines.OffenseRecordRowWithNumber(report, state).is_enabled()


def test_offense_record_row__enabled(report, state):
    state.offense_num = 1
    state.section = Section.DISTRICT_OFFENSE
    assert lines.OffenseRecordRow(report, state).is_enabled()
