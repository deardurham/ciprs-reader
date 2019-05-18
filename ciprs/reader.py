import json
import subprocess

from ciprs import parsers


class PDFToTextReader:

    report = {
        'General': {},
        'Case Information': {},
        'Defendant': {},
        'Offense Record': {
            'Records': [],
        },
    }
    document_parsers = (
        parsers.CaseDetails(report),
        parsers.CaseStatus(report),
        parsers.OffenseRecordRow(report),
        parsers.OffenseDateTime(report),
        parsers.OffenseDisposedDate(report),
        parsers.OffenseDispositionMethod(report),
        parsers.DefendentName(report),
        parsers.DefendentRace(report),
        parsers.DefendentSex(report),
        parsers.DefendentDOB(report),
    )

    def __init__(self, path):
        self.path = path

    def convert_to_text(self):
        run = subprocess.run(
            f"pdftotext -layout -enc UTF-8 {self.path} -",
            check=True,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        return run.stdout.decode("utf-8")

    def parse(self):
        text = self.convert_to_text()
        reader = Reader(text)
        while reader.next() is not None:
            for parser in self.document_parsers:
                parser.find(reader)

    def json(self):
        return json.dumps(self.report, indent=4)


class Reader:

    def __init__(self, source):
        self.source = source
        self.lines = iter(source.splitlines())
        self.current = None

    def next(self):
        self.current = next(self.lines, None)
        return self.current

    def __str__(self):
        return self.current or ''
