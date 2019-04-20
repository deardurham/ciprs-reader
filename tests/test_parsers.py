from ciprs import parsers


def test_case_details():
    string = "  Case Details for Court Case DURHAM 00GR000000  "
    matches = parsers.CaseDetails().match(string)
    assert matches is not None, "Regex match failed"
    assert matches["county"] == "DURHAM"
    assert matches["fileno"] == "00GR000000"


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
    assert matches["value"] == "DOE,JON,BOJACK"


def test_defendent_race():
    string = "   Race: WHITE   "
    matches = parsers.DefendentRace().match(string)
    assert matches is not None, "Regex match failed"
    assert matches["value"] == "WHITE"


def test_defendent_sex():
    string = "   Sex: MALE   "
    matches = parsers.DefendentSex().match(string)
    assert matches is not None, "Regex match failed"
    assert matches["value"] == "MALE"


def test_defendent_dob():
    string = """     Date of Birth/Estimated Age:     Driver License Information  \n
       01/01/2000       • License State: NC
    """
    matches = parsers.DefendentDOB().match(string)
    assert matches is not None, "Regex match failed"
    assert matches["value"] == "2000-01-01"


def test_offense_disposed_date():
    string = "      Disposed on: 01/01/2000   "
    matches = parsers.OffenseDisposedDate().match(string)
    assert matches is not None, "Regex match failed"
    assert matches["value"] == "2000-01-01"


def test_offense_disposition_method():
    string = "    Disposition Method: DISPOSED BY JUDGE      Verdict "
    matches = parsers.OffenseDispositionMethod().match(string)
    assert matches is not None, "Regex match failed"
    assert matches["value"] == "DISPOSED BY JUDGE"
