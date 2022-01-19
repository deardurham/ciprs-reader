import json
import pytest

from ciprs_reader.const import ParserMode
from ciprs_reader.reader import PDFToTextReader


@pytest.mark.parametrize(
    "mode",
    [ParserMode.V1, ParserMode.V2],
)
def test_redacted_forms(mode):

    for testname in ["test_redacted_1", "test_redacted_2"]:
        reader = PDFToTextReader(f"tests/test_records/{testname}.pdf", mode=mode)
        reader.parse()
        output_json = json.loads(reader.json())

        with open(f"tests/test_records/expected_output/{testname}.json", 'r', encoding='utf8') as file:
            expected_output = json.load(file)

        assert output_json, "Unable to parse expected output"
        assert expected_output, "Unable to parse expected output"

        for index, document in enumerate(output_json):
            for section, value in document.items():
                if section not in ['District Court Offense Information', 'Superior Court Offense Information']:
                    assert value == expected_output[index][section], "Section does not match expected output"
                    continue

                # ParserMode.V1 does not handle multiline offense descriptions. Ensure that's the case.
                for offense_index, offense in enumerate(value):
                    expected_offense = expected_output[index][section][offense_index]
                    is_multiline = expected_offense.pop('_multiline', False)
                    if mode == ParserMode.V1 and is_multiline:
                        assert offense != expected_offense
                    else:
                        assert offense == expected_offense


@pytest.mark.parametrize(
    "mode",
    [ParserMode.V1, ParserMode.V2],
)
def test_save_source(mode):
    reader = PDFToTextReader("tests/test_records/test_redacted_1.pdf", mode=mode)
    reader.parse(save_source=True)
    output_json = json.loads(reader.json())
    assert len(output_json) == 1 and output_json[0]['_meta']['source']
