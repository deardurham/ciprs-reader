import pytest

from ciprs_reader.parser.section import header


CASE_DETAIL_DATA = [
    (
        {"county": "DURHAM", "fileno": "00GR000000"},
        "  Case Details for Court Case DURHAM 00GR000000  ",
    ),
    (
        {"county": "ORANGE", "fileno": "99FN9999999"},
        " Case Summary for Court Case: ORANGE 99FN9999999",
    ),
]


@pytest.mark.parametrize("expected, val", CASE_DETAIL_DATA)
def test_case_details(expected, val, report, state):
    matches = header.CaseDetails(report, state).match(val)
    assert matches is not None, "Regex match failed"
    assert matches == expected


def test_defendent_name(report, state):
    string = "   Defendant:   DOE,JON,BOJACK   "
    matches = header.DefendantName(report, state).match(string)
    assert matches is not None, "Regex match failed"
    assert matches["value"] == "JON BOJACK DOE"


def test_defendent_name_no_middle(report, state):
    string = "  Defendant: DOE,JON   "
    matches = header.DefendantName(report, state).match(string)
    assert matches is not None, "Regex match failed"
    assert matches["value"] == "JON DOE"


def test_defendent_name_special_character(report, state):
    string = " Defendant: DOE,JON'BO,JACK"
    matches = header.DefendantName(report, state).match(string)
    assert matches is not None, "Regex match failed"
    assert matches["value"] == "JON'BO JACK DOE"
    string2 = " Defendant: ZACHARY,ERIC-JAZZ,TEST"
    matches = header.DefendantName(report, state).match(string2)
    assert matches is not None, "Regex match failed"
    assert matches["value"] == "ERIC-JAZZ TEST ZACHARY"
