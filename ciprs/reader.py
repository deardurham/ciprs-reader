import json
import logging
import subprocess

from ciprs.parsers import (
    CaseDetails,
    CaseStatus,
    OffenseRecordRow,
    OffenseRecordRowWithNumber,
    OffenseDateTime,
    OffenseDisposedDate,
    CaseWasServedOnDate,
    OffenseDispositionMethod,
    DefendentName,
    DefendentRace,
    DefendentSex,
    DefendentDOB,
    DistrictSuperiorCourt,
)


logger = logging.getLogger(__name__)


class PDFToTextReader:
    def __init__(self, path):
        self.path = path
        self.report = {
            "General": {},
            "Case Information": {},
            "Defendant": {},
            "Offense Record": {"Records": []},
            "_meta": {},
        }
        self.line_parsers = (
            CaseDetails(self.report),
            CaseStatus(self.report),
            OffenseRecordRow(self.report),
            OffenseRecordRowWithNumber(self.report),
            OffenseDateTime(self.report),
            OffenseDisposedDate(self.report),
            CaseWasServedOnDate(self.report),
            OffenseDispositionMethod(self.report),
            DefendentName(self.report),
            DefendentRace(self.report),
            DefendentSex(self.report),
        )
        self.document_parsers = (
            DefendentDOB(self.report),
            DistrictSuperiorCourt(self.report),
        )

    def convert_to_text(self):
        run = subprocess.run(
            f"pdftotext -layout -enc UTF-8 {self.path} -",
            check=True,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        return run.stdout.decode("utf-8")

    def parse(self, source=False):
        text = self.convert_to_text()
        if source:
            # save output of pdftotext for later inspection, if desired
            self.report["_meta"]["source"] = text
        logger.debug("pdftotext: %s", text)
        reader = Reader(text)
        while reader.next() is not None:
            for parser in self.line_parsers:
                parser.find(reader)
        for parser in self.document_parsers:
            parser.find(reader.source)

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
        return self.current or ""
