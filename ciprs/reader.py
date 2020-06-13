import json
import collections
import logging
import subprocess

from ciprs.parser.lines import (
    CaseDetails,
    CaseStatus,
    OffenseRecordRow,
    OffenseRecordRowWithNumber,
    OffenseDateTime,
    OffenseDate,
    OffenseDisposedDate,
    CaseWasServedOnDate,
    OffenseDispositionMethod,
    DefendentName,
    DefendentRace,
    DefendentSex,
    DefendentDOB,
    DistrictSuperiorCourt,
)

from ciprs.parser import section
from ciprs.parser.offense import Offenses


logger = logging.getLogger(__name__)


def json_default(obj):
    try:
        return obj.__json__()
    except AttributeError:
        raise TypeError("{} can not be JSON encoded".format(type(obj)))


class PDFToTextReader:
    def __init__(self, path):
        self.path = path
        self.report = {
            "General": {},
            "Case Information": {},
            "Defendant": {},
            "Offense Record": {"Records": []},
            "District Court Offense Information": Offenses(),
            "Superior Court Offense Information": Offenses(),
            "_meta": {},
        }
        state = collections.defaultdict(str)
        self.line_parsers = (
            section.CaseInformation(self.report, state),
            section.DistrictCourtOffenseSection(self.report, state),
            # CaseDetails(self.report),
            # CaseStatus(self.report),
            OffenseRecordRow(self.report, state),
            OffenseRecordRowWithNumber(self.report, state),
            # OffenseDate(self.report),
            # OffenseDateTime(self.report),
            OffenseDisposedDate(self.report, state),
            # CaseWasServedOnDate(self.report),
            OffenseDispositionMethod(self.report, state),
            # DefendentName(self.report),
            # DefendentRace(self.report),
            # DefendentSex(self.report),
        )
        self.document_parsers = (
            DefendentDOB(self.report, state),
            DistrictSuperiorCourt(self.report, state),
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
        return json.dumps(self.report, indent=4, default=json_default)


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
