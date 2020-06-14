import pytest

from ciprs_reader.parser.section import case_information


def test_case_status(report, state):
    string = "  Case Status: DISPOSED  "
    matches = case_information.CaseStatus(report, state).match(string)
    assert matches is not None, "Regex match failed"
    assert matches["value"] == "DISPOSED"


def test_offense_date_time(report, state):
    string = "    Offense Date/Time: 05/17/2015 09:59 PM   "
    matches = case_information.OffenseDateTime(report, state).match(string)
    assert matches is not None, "Regex match failed"
    assert matches["value"] == "2015-05-17T21:59:00"


@pytest.mark.parametrize(
    "expected,val",
    (
        ("2000-09-09", "    Case Was Served on: 09/09/2000   "),
        ("2015-05-17", "Case Was Reinstated: -    Case Was Served on: 05/17/2015"),
    ),
)
def test_case_was_served_on_date(expected, val, report, state):
    matches = case_information.CaseWasServedOnDate(report, state).match(val)
    assert matches is not None, "Regex match failed"
    assert matches["value"] == expected


def test_offense_date(report, state):
    string = "    Offense Date: 11/28/2005   • Date: 04/13/2006"
    matches = case_information.OffenseDate(report, state).match(string)
    assert matches is not None, "Regex match failed"
    assert matches["value"] == "2005-11-28T00:00:00"
