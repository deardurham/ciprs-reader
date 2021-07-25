from dataclasses import dataclass

from ciprs_reader.const import Section
from ciprs_reader.parser.base import Parser


@dataclass
class ParserState:
    """Object to maintain state while parsing CIPRS record."""

    section: str = Section.HEADER
    offense_num: int = 0


class RecordSection(Parser):
    """Parser that only looks for CIPRS record section headers and sets state."""

    def set_state(self, state):
        state.section = self.matches

    def match(self, document):
        self.matches = None
        self.document = document
        matches = self.re.match(str(document))
        if matches:
            self.matches = self.clean(matches)
        return self.matches

    def extract(self, matches, report):
        pass


class CaseInformation(RecordSection):

    pattern = r"^\s*Case Information\s*$"

    def clean(self, matches):
        return Section.CASE_INFORMATION


class DefendantSection(RecordSection):

    # Handles two cases of xpdfreader parsing
    # 1: "Defendant Section being on a line with no other text
    # 2: "First Alias" appearing after "Defendant" section header on same line
    pattern = r"^\s*Defendant(?:\s|$)"

    def clean(self, matches):
        return Section.DEFENDANT


class DistrictCourtOffenseSection(RecordSection):

    pattern = r"^\s*District Court Offense Information\s*$"

    def clean(self, matches):
        return Section.DISTRICT_OFFENSE


class SuperiorCourtOffenseSection(RecordSection):

    pattern = r"^\s*Superior Court Offense Information\s*$"

    def clean(self, matches):
        return Section.SUPERIOR_OFFENSE


class DisclaimerSection(RecordSection):

    pattern = r"^\s*Disclaimer\s*$"

    def clean(self, matches):
        return "Disclaimer"
