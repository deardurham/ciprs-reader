import pytest

from ciprs_reader.parser import lines as parsers


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
