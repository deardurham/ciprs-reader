import pytest

from ciprs_reader.parser import lines as parsers, state as state_parsers


def test_defendent_dob(report, state):
    string = """     Date of Birth/Estimated Age:     Driver License Information  \n
       01/01/2000       • License State: NC
    """
    matches = parsers.DefendentDOB(report, state).match(string)
    assert matches is not None, "Regex match failed"
    assert matches["value"] == "2000-01-01"


def test_court_type_other(report, state):
    report = {"General": {"File No": "11XX777777"}}
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


def test_court_type_if(report, state):
    report = {"General": {"File No": "11IF777777"}}
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

@pytest.mark.parametrize(
    "document,parser",
    [
        (
            "Not a certified copy. ~Not a certified copy. ~  District Court    Offense Information",
            state_parsers.DistrictCourtOffenseSection,
        ),
        (
            "Not a certified copy. ~Not a certified copy. ~  Superior    Court Offense    Information",
            state_parsers.SuperiorCourtOffenseSection,
        )
    ],
)
def test_offense_parsers__search_section(document, parser, report, state):
    assert parser(report, state).match(document) is not None
