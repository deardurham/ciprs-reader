import json
import logging
import subprocess

from ciprs_reader.parser.state import ParserState
from ciprs_reader.parser.models import Offenses
from ciprs_reader.reader.parsers import DOCUMENT_PARSERS, LINE_PARSERS


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
            "District Court Offense Information": Offenses(),
            "Superior Court Offense Information": Offenses(),
            "_meta": {},
        }
        state = ParserState()
        self.line_parsers = []
        for parser in LINE_PARSERS:
            self.line_parsers.append(parser(self.report, state))
        self.document_parsers = []
        for parser in DOCUMENT_PARSERS:
            self.document_parsers.append(parser(self.report, state))

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
