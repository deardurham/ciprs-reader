import json
import subprocess

from ciprs import parsers


class PDFToTextReader:

    report = {
        'General': {},
        'Case Information': {},
        'Case Officials': {},
        'Arrest and Release Information': {},
        'Violation of Court Orders': {},
        'Defendant': {},
        'Witnesses': {},
        'Citation Information': {},
        'Consolidation for Judgment': {},
        'Offense Record': {
            'Records': [],
            'Court Officials': {},
            'Violation of Court Orders': {},
            'Transfers or Appeals': {},
            'Monies': {},
        },
        'DMV Notification Events': {},
    }
    document_parsers = (
        parsers.CaseDetails(report),
        parsers.CaseStatus(report),
        parsers.OffenseRecordRow(report),
        parsers.OffenseDateTime(report),
        parsers.DefendentName(report),
        parsers.DefendentRace(report),
        parsers.DefendentSex(report),
    )

    def __init__(self, path):
        self.path = path
        self.text = ''

    def convert_to_text(self):
        run = subprocess.run(
            f"pdftotext -layout -enc UTF-8 {self.path} -",
            capture_output=True,
            check=True,
            shell=True,
        )
        self.text = run.stdout.decode("utf-8")
        return self.text

    def parse(self):
        self.convert_to_text()
        reader = Reader(iter(self.text.splitlines()))
        while reader.next() is not None:
            for parser in self.document_parsers:
                parser.find(reader)

    def json(self):
        return json.dumps(self.report, indent=4)


class Reader:

    def __init__(self, source):
        self.source = source
        self.current = None

    def next(self):
        self.current = next(self.source, None)
        return self.current

    def __str__(self):
        return self.current or ''
