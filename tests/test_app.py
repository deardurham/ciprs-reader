import json
from ciprs_reader.reader import PDFToTextReader

EXPECTED_OUTPUT = [{
    "General": {
        "County": "DURHAM",
        "File No": "88CR0121",
        "District": "Yes"
    },
    "Case Information": {
        "Case Status": "DISPOSED",
        "Offense Date": "1988-05-01T00:00:00",
        "Arrest Date": "1988-05-01"
    },
    "Defendant": {
        "Name": "YA",
        "Race": "WHITE",
        "Sex": "F",
        "Date of Birth/Estimated Age": ""
    },
    "District Court Offense Information": [
        {
            "Records": [
                {
                    "Action": "CHARGED",
                    "Description": "POSSESS MARIJUANA UP TO 1/2 OZ",
                    "Severity": "MISDEMEANOR",
                    "Law": "G.S. 90-95(D)(4)"
                }
            ],
            "Disposed On": "1988-10-07",
            "Disposition Method": "DISMISSAL WITHOUT LEAVE BY DA"
        }
    ],
    "Superior Court Offense Information": [],
    "_meta": {}
}]

def test_redacted_form():
    reader = PDFToTextReader("tests/test_records/test_redacted.pdf")
    reader.parse()
    output_json = json.loads(reader.json())

    for index, document in enumerate(output_json):
        for section, value in document.items():
            assert value == EXPECTED_OUTPUT[index][section], f"Section '{section}' does not match expected output"
