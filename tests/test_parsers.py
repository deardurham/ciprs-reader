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
