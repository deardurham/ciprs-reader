import pytest

from ciprs_reader.parser import lines as parsers

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
    matches = parsers.CaseDetails(report, state).match(val)
    assert matches is not None, "Regex match failed"
    assert matches == expected


def test_case_status(report, state):
    string = "  Case Status: DISPOSED  "
    matches = parsers.CaseStatus(report, state).match(string)
    assert matches is not None, "Regex match failed"
    assert matches["value"] == "DISPOSED"


def test_offense_record_charged(report, state):
    string = "CHARGED       SPEEDING(80 mph in a 65 mph zone)    INFRACTION    G.S. 20-141(B)"  # noqa
    matches = parsers.OffenseRecordRow(report, state).match(string)
    assert matches is not None, "Regex match failed"
    assert matches["action"] == "CHARGED"
    assert matches["desc"] == "SPEEDING(80 mph in a 65 mph zone)"
    assert matches["severity"] == "INFRACTION"
    assert matches["law"] == "G.S. 20-141(B)"


@pytest.mark.parametrize(
    "line",
    (
        "54  CHARGED       SPEEDING(80 mph in a 65 mph zone)    INFRACTION    G.S. 20-141(B)",
        "  54  CHARGED       SPEEDING(80 mph in a 65 mph zone)    INFRACTION    G.S. 20-141(B)   ",
    ),
)
def test_offense_record_charged_with_number(line, report, state):
    matches = parsers.OffenseRecordRowWithNumber(report, state).match(line)
    assert matches is not None, "Regex match failed"
    assert matches["action"] == "CHARGED"
    assert matches["desc"] == "SPEEDING(80 mph in a 65 mph zone)"
    assert matches["severity"] == "INFRACTION"
    assert matches["law"] == "G.S. 20-141(B)"


def test_offense_record_arrainged(report, state):
    string = "ARRAIGNED SPEEDING(80 mph in a 65 mph zone)        INFRACTION    G.S. 20-141(B)"  # noqa
    matches = parsers.OffenseRecordRow(report, state).match(string)
    assert matches is not None, "Regex match failed"
    assert matches["action"] == "ARRAIGNED"
    assert matches["desc"] == "SPEEDING(80 mph in a 65 mph zone)"
    assert matches["severity"] == "INFRACTION"
    assert matches["law"] == "G.S. 20-141(B)"


def test_offense_record_convicted(report, state):
    string = "CONVICTED IMPROPER EQUIP - SPEEDOMETER             INFRACTION    G.S. 20-123.2"  # noqa
    matches = parsers.OffenseRecordRow(report, state).match(string)
    assert matches is not None, "Regex match failed"
    assert matches["action"] == "CONVICTED"
    assert matches["desc"] == "IMPROPER EQUIP - SPEEDOMETER"
    assert matches["severity"] == "INFRACTION"
    assert matches["law"] == "G.S. 20-123.2"


def test_offense_date_time(report, state):
    string = "    Offense Date/Time: 05/17/2015 09:59 PM   "
    matches = parsers.OffenseDateTime(report, state).match(string)
    assert matches is not None, "Regex match failed"
    assert matches["value"] == "2015-05-17T21:59:00"


def test_defendent_name(report, state):
    string = "   Defendant:   DOE,JON,BOJACK   "
    matches = parsers.DefendantName(report, state).match(string)
    assert matches is not None, "Regex match failed"
    assert matches["value"] == "JON BOJACK DOE"


def test_defendent_name_no_middle(report, state):
    string = "  Defendant: DOE,JON   "
    matches = parsers.DefendantName(report, state).match(string)
    assert matches is not None, "Regex match failed"
    assert matches["value"] == "JON DOE"


def test_defendent_name_special_character(report, state):
    string = " Defendant: DOE,JON'BO,JACK"
    matches = parsers.DefendantName(report, state).match(string)
    assert matches is not None, "Regex match failed"
    assert matches["value"] == "JON'BO JACK DOE"
    string2 = " Defendant: ZACHARY,ERIC-JAZZ,TEST"
    matches = parsers.DefendantName(report, state).match(string2)
    assert matches is not None, "Regex match failed"
    assert matches["value"] == "ERIC-JAZZ TEST ZACHARY"


def test_defendent_race(report, state):
    string = "   Race: WHITE   "
    matches = parsers.DefendantRace(report, state).match(string)
    assert matches is not None, "Regex match failed"
    assert matches["value"] == "WHITE"


def test_defendent_sex_male(report, state):
    string = "   Sex: MALE   "
    matches = parsers.DefendantSex(report, state).match(string)
    assert matches is not None, "Regex match failed"
    assert matches["value"] == "M"


def test_defendent_sex_female(report, state):
    string = "   Sex: FEMALE   "
    matches = parsers.DefendantSex(report, state).match(string)
    assert matches is not None, "Regex match failed"
    assert matches["value"] == "F"


def test_defendent_sex_bad(report, state):
    string = "   Sex: DUNNO   "
    matches = parsers.DefendantSex(report, state).match(string)
    assert matches is not None, "Regex match failed"
    assert matches["value"] == ""


def test_defendent_dob(report, state):
    string = """     Date of Birth/Estimated Age:     Driver License Information  \n
       01/01/2000       • License State: NC
    """
    matches = parsers.DefendentDOB(report, state).match(string)
    assert matches is not None, "Regex match failed"
    assert matches["value"] == "2000-01-01"


@pytest.mark.parametrize(
    "expected,val",
    (
        ("2000-01-01", "      Disposed on: 01/01/2000   "),
        (
            "2016-07-20",
            "    Plea: RESPONSIBLE                         Verdict: RESPONSIBLE             Disposed on: 07/20/2016   ",
        ),
    ),
)
def test_offense_disposed_date(expected, val, report, state):
    matches = parsers.OffenseDisposedDate(report, state).match(val)
    assert matches is not None, "Regex match failed"
    assert matches["value"] == expected


@pytest.mark.parametrize(
    "expected,val",
    (
        ("2000-09-09", "    Case Was Served on: 09/09/2000   "),
        ("2015-05-17", "Case Was Reinstated: -    Case Was Served on: 05/17/2015"),
    ),
)
def test_case_was_served_on_date(expected, val, report, state):
    matches = parsers.CaseWasServedOnDate(report, state).match(val)
    assert matches is not None, "Regex match failed"
    assert matches["value"] == expected


def test_known_offense_disposition_method(report, state):
    string = "    Disposition Method: DISPOSED BY JUDGE"
    matches = parsers.OffenseDispositionMethod(report, state).match(string)
    assert matches is not None, "Regex match failed"
    assert matches["value"] == "DISPOSED BY JUDGE"


def test_court_type_other(report, state):
    report = {"General": {"File No": "11IF777777"}}
    matches = parsers.DistrictSuperiorCourt(report, state).match("")
    assert matches is not None, "Regex match failed"
    assert matches == {}


def test_court_type_cr(report, state):
    report = {"General": {"File No": "11CR777777"}}
    parser = parsers.DistrictSuperiorCourt(report, state)
    parser.find("")
    assert parser.matches is not None, "Regex match failed"
    assert parser.matches == {"District": "Yes"}
    assert report["General"]["District"] == "Yes"


def test_court_type_crs(report, state):
    report = {"General": {"File No": "11CRS777777"}}
    parser = parsers.DistrictSuperiorCourt(report, state)
    parser.find("")
    assert parser.matches is not None, "Regex match failed"
    assert parser.matches == {"Superior": "Yes"}
    assert report["General"]["Superior"] == "Yes"


def test_offense_date(report, state):
    string = "    Offense Date: 11/28/2005   • Date: 04/13/2006"
    matches = parsers.OffenseDate(report, state).match(string)
    assert matches is not None, "Regex match failed"
    assert matches["value"] == "2005-11-28T00:00:00"
