from dataclasses import dataclass

from ciprs_reader.const import Section
from ciprs_reader.parser.base import Parser


@dataclass
class ParserState:
    """Object to maintain state while parsing CIPRS record."""

    section: str = Section.HEADER
    offense_num: int = 0
    is_desc_ext_possible: bool = False


class RecordSection(Parser):
    """Parser that only looks for CIPRS record section headers and sets state."""

    def set_state(self, state):
        state.section = self.matches

    def match(self, document):
        self.matches = None
        self.document = document
        if self.re_method == "match":
            matches = self.re.match(str(document))
        else:
            matches = self.re.search(str(document))
        if matches:
            self.matches = self.clean(matches)
        return self.matches

    def extract(self, matches, report):
        pass


class CaseInformation(RecordSection):

    pattern = [r"\s*Case", r"Information$"]

    def clean(self, matches):
        return Section.CASE_INFORMATION


class DefendantSection(RecordSection):

    pattern = r"\s*Defendant$"

    def clean(self, matches):
        return Section.DEFENDANT


class DistrictCourtOffenseSection(RecordSection):

    re_method = "search"
    pattern = [r"\s*District", "Court", "Offense", r"Information$"]

    def clean(self, matches):
        return Section.DISTRICT_OFFENSE


class SuperiorCourtOffenseSection(RecordSection):

    re_method = "search"
    pattern = [r"\s*Superior", "Court", "Offense", r"Information$"]

    def clean(self, matches):
        return Section.SUPERIOR_OFFENSE
