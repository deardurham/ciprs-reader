from ciprs_reader.parser.base import Parser
from ciprs_reader.const import Section
from ciprs_reader.parser.section.offense import OFFENSE_SECTION_PARSERS
from lark import Lark

class OffenseSectionParser:
    """Only enabled when in offense-related sections."""

    def __init__(self, report, state):
        self.state = state
        self.section_lines = []
        self.parser = Lark(r"""
            section      : (disposition_method | jurisdiction | info | records | garbage | _NEWLINE)*

            disposition_method : "Disposition" "Method:" TEXT+
            jurisdiction : "Current" "Jurisdiction:" WORD+
            info         : "Plea:" plea "Verdict:" verdict "Disposed" "on:" disposed_on
            records      : record ~ 2
            record       : record_num? action description severity law _NEWLINE (description_ext _NEWLINE)*
            garbage      : TEXT+ _NEWLINE

            plea: "-" | WORD+
            verdict: "-" | WORD+
            disposed_on: "-" | TEXT+

            record_num   : INT
            action       : ACTION
            description  : "-" | TEXT+
            description_ext : (/(?!Plea:)\S+/)+
            severity     : "-" | SEVERITY
            law          : "-" | /\S[\S ]+\S/

            ACTION       : "CHARGED"
                            | "CONVICTED"
                            | "ARRAIGNED"

            SEVERITY     : "TRAFFIC"
                            | "INFRACTION"
                            | "MISDEMEANOR"
                            | "FELONY"

            TEXT         : (/\S+/)+
            _NEWLINE     : NEWLINE

            %import common.INT
            %import common.WORD
            %import common.WS_INLINE
            %import common.NEWLINE
            %ignore WS_INLINE
        """, start='section')

    def parse_section(self):
        print(self.parser.parse("\n".join(self.section_lines)).pretty())


class DistrictCourtOffenseSection(OffenseSectionParser):
    def is_enabled(self):
        return self.state.section == Section.DISTRICT_OFFENSE


class SuperiorCourtOffenseSection(OffenseSectionParser):
    def is_enabled(self):
        return self.state.section == Section.SUPERIOR_OFFENSE
