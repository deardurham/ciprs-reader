from ciprs_reader.parser.section import defendant


def test_defendent_race(report, state):
    string = "   Race: WHITE   "
    matches = defendant.DefendantRace(report, state).match(string)
    assert matches is not None, "Regex match failed"
    assert matches["value"] == "WHITE"


def test_defendent_sex_male(report, state):
    string = "   Sex: MALE   "
    matches = defendant.DefendantSex(report, state).match(string)
    assert matches is not None, "Regex match failed"
    assert matches["value"] == "M"


def test_defendent_sex_female(report, state):
    string = "   Sex: FEMALE   "
    matches = defendant.DefendantSex(report, state).match(string)
    assert matches is not None, "Regex match failed"
    assert matches["value"] == "F"


def test_defendent_sex_bad(report, state):
    string = "   Sex: DUNNO   "
    matches = defendant.DefendantSex(report, state).match(string)
    assert matches is not None, "Regex match failed"
    assert matches["value"] == ""
