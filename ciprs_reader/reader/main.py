import json
import logging
import subprocess

from ciprs_reader.parser.state import ParserState
from ciprs_reader.parser.models import Offenses
from ciprs_reader.reader.parsers import DOCUMENT_PARSERS, LINE_PARSERS
from ciprs_reader.reader.util import json_default, Reader


logger = logging.getLogger(__name__)


class PDFToTextReader:
    """Read PDF and perform entity extraction using parsers."""

    def __init__(self, path):
        self.path = path
        # skelton JSON structure for parser-extracted entities
        self.report = {
            "General": {},
            "Case Information": {},
            "Defendant": {},
            "District Court Offense Information": Offenses(),
            "Superior Court Offense Information": Offenses(),
            "_meta": {},
        }
        # object that stores state that's accessible between parsers
        self.state = ParserState()
        # line parsers are run against every line within a document
        self.line_parsers = []
        for parser in LINE_PARSERS:
            self.line_parsers.append(parser(self.report, self.state))
        self.document_parsers = []
        # document parsers are run once against an entire document
        for parser in DOCUMENT_PARSERS:
            self.document_parsers.append(parser(self.report, self.state))

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
        # pylint: disable=not-callable
        while reader.next() is not None:
            for parser in self.line_parsers:
                parser.find(reader)
        for parser in self.document_parsers:
            parser.find(reader.source)

    def json(self):
        return json.dumps(self.report, indent=4, default=json_default)
