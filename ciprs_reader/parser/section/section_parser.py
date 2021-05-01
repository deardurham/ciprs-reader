from ciprs_reader.parser.base import Parser
from ciprs_reader.const import Section
from ciprs_reader.parser.section.offense import OFFENSE_SECTION_PARSERS

class OffenseSectionParser:
    """Only enabled when in offense-related sections."""

    def __init__(self, report, state):
        self.parsers = []
        self.state = state
        self.section_lines = []
        for parser in OFFENSE_SECTION_PARSERS:
            self.parsers.append(parser(report, state, multiline=True))

    def parse_section(self):
        for parser in self.parsers:
            parser.find("\n".join(self.section_lines))


class DistrictCourtOffenseSection(OffenseSectionParser):
    def is_enabled(self):
        return self.state.section == Section.DISTRICT_OFFENSE

    def parse_section(self):
        self.state.section = Section.DISTRICT_OFFENSE
        super().parse_section()


class SuperiorCourtOffenseSection(OffenseSectionParser):
    def is_enabled(self):
        return self.state.section == Section.SUPERIOR_OFFENSE

    def parse_section(self):
        self.state.section = Section.SUPERIOR_OFFENSE
        super().parse_section()
