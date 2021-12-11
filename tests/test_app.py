import json
import pytest

from ciprs_reader.const import ParserMode
from ciprs_reader.reader import PDFToTextReader


@pytest.mark.parametrize(
    "testname",
    ["test_redacted_1", "test_redacted_2"],
)
def test_redacted_forms_v1(testname):
    reader = PDFToTextReader(f"tests/test_records/{testname}.pdf", mode=ParserMode.V1)
    reader.parse()
    output_json = json.loads(reader.json())

    with open(f"tests/test_records/expected_output/{testname}.json", 'r') as file:
        expected_output = json.load(file)
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
    for index, document in enumerate(output_json):
        for section, value in document.items():
            assert value == expected_output[index][section], f"Section '{section}' does not match expected output"
