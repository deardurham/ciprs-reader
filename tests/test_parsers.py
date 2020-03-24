import pytest

from ciprs import parsers

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
def test_case_details(expected, val):
    matches = parsers.CaseDetails().match(val)
    assert matches is not None, "Regex match failed"
    assert matches == expected


def test_case_status():
    string = "  Case Status: DISPOSED  "
    matches = parsers.CaseStatus().match(string)
    assert matches is not None, "Regex match failed"
    assert matches["value"] == "DISPOSED"


def test_offense_record_charged():
    string = "CHARGED       SPEEDING(80 mph in a 65 mph zone)    INFRACTION    G.S. 20-141(B)    4450"  # noqa
    matches = parsers.OffenseRecordRow().match(string)
    assert matches is not None, "Regex match failed"
    assert matches["action"] == "CHARGED"
    assert matches["desc"] == "SPEEDING(80 mph in a 65 mph zone)"
    assert matches["severity"] == "INFRACTION"
    assert matches["law"] == "G.S. 20-141(B)"
    assert matches["code"] == "4450"


@pytest.mark.parametrize(
    "line",
    (
        "54  CHARGED       SPEEDING(80 mph in a 65 mph zone)    INFRACTION    G.S. 20-141(B)",
        "  54  CHARGED       SPEEDING(80 mph in a 65 mph zone)    INFRACTION    G.S. 20-141(B)   ",
    ),
)
def test_offense_record_charged_with_number(line):
    matches = parsers.OffenseRecordRowWithNumber().match(line)
    assert matches is not None, "Regex match failed"
    assert matches["action"] == "CHARGED"
    assert matches["desc"] == "SPEEDING(80 mph in a 65 mph zone)"
    assert matches["severity"] == "INFRACTION"
    assert matches["law"] == "G.S. 20-141(B)"


def test_offense_record_arrainged():
    string = "ARRAIGNED SPEEDING(80 mph in a 65 mph zone)        INFRACTION    G.S. 20-141(B)    4450"  # noqa
    matches = parsers.OffenseRecordRow().match(string)
    assert matches is not None, "Regex match failed"
    assert matches["action"] == "ARRAIGNED"
    assert matches["desc"] == "SPEEDING(80 mph in a 65 mph zone)"
    assert matches["severity"] == "INFRACTION"
    assert matches["law"] == "G.S. 20-141(B)"
    assert matches["code"] == "4450"


def test_offense_record_convicted():
    string = "CONVICTED IMPROPER EQUIP - SPEEDOMETER             INFRACTION    G.S. 20-123.2     4418"  # noqa
    matches = parsers.OffenseRecordRow().match(string)
    assert matches is not None, "Regex match failed"
    assert matches["action"] == "CONVICTED"
    assert matches["desc"] == "IMPROPER EQUIP - SPEEDOMETER"
    assert matches["severity"] == "INFRACTION"
    assert matches["law"] == "G.S. 20-123.2"
    assert matches["code"] == "4418"


def test_offense_date_time():
    string = "    Offense Date/Time: 05/17/2015 09:59 PM   "
    matches = parsers.OffenseDateTime().match(string)
    assert matches is not None, "Regex match failed"
    assert matches["value"] == "2015-05-17T21:59:00"


def test_defendent_name():
    string = "   Defendant:   DOE,JON,BOJACK   "
    matches = parsers.DefendentName().match(string)
    assert matches is not None, "Regex match failed"
    assert matches["value"] == "JON BOJACK DOE"


def test_defendent_name_no_middle():
    string = "  Defendant: DOE,JON   "
    matches = parsers.DefendentName().match(string)
    assert matches is not None, "Regex match failed"
    assert matches["value"] == "JON DOE"


def test_defendent_race():
    string = "   Race: WHITE   "
    matches = parsers.DefendentRace().match(string)
    assert matches is not None, "Regex match failed"
    assert matches["value"] == "WHITE"


def test_defendent_sex_male():
    string = "   Sex: MALE   "
    matches = parsers.DefendentSex().match(string)
    assert matches is not None, "Regex match failed"
    assert matches["value"] == "M"


def test_defendent_sex_female():
    string = "   Sex: FEMALE   "
    matches = parsers.DefendentSex().match(string)
    assert matches is not None, "Regex match failed"
    assert matches["value"] == "F"


def test_defendent_sex_bad():
    string = "   Sex: DUNNO   "
    matches = parsers.DefendentSex().match(string)
    assert matches is not None, "Regex match failed"
    assert matches["value"] == ""


def test_defendent_dob():
    string = """     Date of Birth/Estimated Age:     Driver License Information  \n
       01/01/2000       • License State: NC
    """
    matches = parsers.DefendentDOB().match(string)
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
def test_offense_disposed_date(expected, val):
    matches = parsers.OffenseDisposedDate().match(val)
    assert matches is not None, "Regex match failed"
    assert matches["value"] == expected


@pytest.mark.parametrize(
    "expected,val",
    (
        ("2000-09-09", "    Case Was Served on: 09/09/2000   "),
        ("2015-05-17", "Case Was Reinstated: -    Case Was Served on: 05/17/2015"),
    ),
)
def test_case_was_served_on_date(expected, val):
    matches = parsers.CaseWasServedOnDate().match(val)
    assert matches is not None, "Regex match failed"
    assert matches["value"] == expected


def test_known_offense_disposition_method():
    string = "    Disposition Method: DISPOSED BY JUDGE      Verdict "
    matches = parsers.OffenseDispositionMethod().match(string)
    assert matches is not None, "Regex match failed"
    assert matches["value"] == "JU"


def test_unknown_offense_disposition_method():
    string = "   Disposition Method: PROBATION OTHER     Verdict"
    matches = parsers.OffenseDispositionMethod().match(string)
    assert matches is not None, "Regex match failed"
    assert matches["value"] == "PROBATION OTHER"


def test_court_type_other():
    report = {"General": {"File No": "11IF777777"}}
    matches = parsers.DistrictSuperiorCourt(report).match("")
    assert matches is not None, "Regex match failed"
    assert matches == {}


def test_court_type_cr():
    report = {"General": {"File No": "11CR777777"}}
    parser = parsers.DistrictSuperiorCourt(report)
    parser.find("")
    assert parser.matches is not None, "Regex match failed"
    assert parser.matches == {"District": "Yes"}
    assert report["General"]["District"] == "Yes"


def test_court_type_crs():
    report = {"General": {"File No": "11CRS777777"}}
    parser = parsers.DistrictSuperiorCourt(report)
    parser.find("")
    assert parser.matches is not None, "Regex match failed"
    assert parser.matches == {"Superior": "Yes"}
    assert report["General"]["Superior"] == "Yes"


def test_offense_date():
    string = "    Offense Date: 11/28/2005   • Date: 04/13/2006"
    matches = parsers.OffenseDate().match(string)
    assert matches is not None, "Regex match failed"
    assert matches["value"] == "2005-11-28T00:00:00"
