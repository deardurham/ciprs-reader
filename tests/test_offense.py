def test_offenses_starts_empty(offenses):
    assert not offenses


def test_offenses_new(offenses):
    offenses.new()
    assert len(offenses) == 1


def test_offenses_current_always_exists(offenses):
    assert offenses.current == {}


def test_add_record(offense):
    record = {"foo": "bar"}
    offense.add_record(record)
    assert offense["Records"][-1] == record


def test_offenses_current_current_record_empty(offenses):
    assert offenses.current.current_record() is None


def test_offenes_current_current_record_with_record(offenses):
    record = {"foo": "bar"}
    offenses.current.add_record(record)
    assert offenses.current.current_record() == record
