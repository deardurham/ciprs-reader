import json
import pytest

from ciprs_reader.const import ParserMode
from ciprs_reader.reader import PDFToTextReader


@pytest.mark.parametrize(
    "is_v1_parsable,testname",
    [(True, "test_redacted_1"), (False, "test_redacted_2")],
)
def test_redacted_forms_v1(is_v1_parsable, testname):
    reader = PDFToTextReader(f"tests/test_records/{testname}.pdf", mode=ParserMode.V1)
    reader.parse()
    output_json = json.loads(reader.json())
    with open(f"tests/test_records/expected_output/{testname}.json", 'r') as file:
        expected_output = json.load(file)

    assert output_json, "Unable to parse expected output"
    assert expected_output, "Unable to parse expected output"

    # test contains multiline text and is not verifiable through expected_output
    # note: we still want to run the above code to make sure ciprs-reader doesn't crash while parsing in V1 mode
    if not is_v1_parsable:
        return

    for index, document in enumerate(output_json):
        for section, value in document.items():
            assert value == expected_output[index][section], f"Section '{section}' does not match expected output"


@pytest.mark.parametrize(
    "testname",
    ["test_redacted_1", "test_redacted_2"],
)
def test_redacted_forms_v2(testname):
    reader = PDFToTextReader(f"tests/test_records/{testname}.pdf", mode=ParserMode.V2)
    reader.parse()
    output_json = json.loads(reader.json())

    with open(f"tests/test_records/expected_output/{testname}.json", 'r') as file:
        expected_output = json.load(file)

    assert output_json, "Unable to parse expected output"
    assert expected_output, "Unable to parse expected output"

    for index, document in enumerate(output_json):
        for section, value in document.items():
            assert value == expected_output[index][section], f"Section '{section}' does not match expected output"


@pytest.mark.parametrize(
    "mode",
    [ParserMode.V1, ParserMode.V2],
)
def test_save_source(mode):
    reader = PDFToTextReader("tests/test_records/test_redacted_1.pdf", mode=mode)
    reader.parse(save_source=True)
    output_json = json.loads(reader.json())
    assert len(output_json) == 1 and output_json[0]['_meta']['source']
