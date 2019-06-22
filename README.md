# CIPRS Reader


## Setup and Run:

Add pdf file to parse in /ignore folder then run:

```bash
docker build -t ciprs-reader .
docker run -v "${PWD}:/usr/src/app" ciprs-reader python ciprs_reader.py ignore/cypress-example.pdf
```

Example output:

```json
{
    "General": {
        "County": "DURHAM",
        "File No": "00GR000000"
    },
    "Case Information": {
        "Case Status": "DISPOSED",
        "Offense Date": "2018-01-01T20:00:00"
    },
    "Defendant": {
        "Date of Birth/Estimated Age": "1990-01-01",
        "Name": "DOE,JON,BOJACK",
        "Race": "WHITE",
        "Sex": "MALE"
    },
    "Offense Record": {
        "Records": [
            {
                "Action": "CHARGED",
                "Description": "SPEEDING(80 mph in a 65 mph zone)",
                "Severity": "INFRACTION",
                "Law": "G.S. 20-141(B)",
                "Code": "4450"
            },
            {
                "Action": "ARRAIGNED",
                "Description": "SPEEDING(80 mph in a 65 mph zone)",
                "Severity": "INFRACTION",
                "Law": "G.S. 20-141(B)",
                "Code": "4450"
            },
            {
                "Action": "CONVICTED",
                "Description": "IMPROPER EQUIP - SPEEDOMETER",
                "Severity": "INFRACTION",
                "Law": "G.S. 20-123.2",
                "Code": "4418"
            }
        ],
        "Disposed On": "2018-02-01",
        "Disposition Method": "DISPOSED BY JUDGE"
    }
}
```

Run Jupyter:

```bash
jupyter-lab
```

Run tests:

```bash
pytest --pylint
```

Code for Durham
