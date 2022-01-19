import datetime as dt
import re

from ciprs_reader.const import Section
from ciprs_reader.parser.base import Parser

ACTION = r"(?:ARRAIGNED|CHARGED|CONVICTED)"
SEVERITY = r"(?:MISDEMEANOR|TRAFFIC|INFRACTION|FELONY)"
GARBAGE_TEXT =r"(?:Printed\s+on )"


class OffenseSectionParser(Parser):
    """Only enabled when in offense-related sections."""

    def is_enabled(self):
        return self.state.section in (
            Section.DISTRICT_OFFENSE,
            Section.SUPERIOR_OFFENSE,
        )


class OffenseRecordRowWithNumber(OffenseSectionParser):
    """
    Extract offense row like:
        54  CHARGED  SPEEDING  INFRACTION  G.S. 20-141(B)
    """

    # pylint: disable=line-too-long
    pattern = r"\s*(?P<num>[\d]+)\s*(?P<action>{action})\s+(?P<desc>.+)[ ]{{2,}}(?P<severity>\w+)[ ]{{2,}}(?P<law>[\w. \-\(\)]+)".format(action=ACTION)

    def set_state(self, state):
        """
        Set offense_num so other parsers, like OffenseRecordRow,
        can use it.
        """
        state.offense_num = self.matches["num"]
        state.is_desc_ext_possible = True

    def clean(self, matches):
        matches['desc'] = re.sub(r' +', ' ', matches['desc'].strip())
        matches['law'] = re.sub(r' +', ' ', matches['law'].strip())
        return matches

    def extract(self, matches, report):
        record = {
            "Action": matches["action"],
            "Description": matches["desc"],
            "Severity": matches["severity"],
            "Law": matches["law"],
        }
        offenses = report[self.state.section]
        # Whenever a row with number is encountered, it indicates a new
        # offense record, so we always add a NEW offense below.
        offenses.new().add_record(record)


class OffenseRecordRow(OffenseSectionParser):
    """
    Extract offense row like:
        CHARGED  SPEEDING  INFRACTION  G.S. 20-141(B)  4450
    """

    # pylint: disable=line-too-long
    pattern = r"\s*(?P<action>{action})\s+(?P<desc>.+)[ ]{{2,}}(?P<severity>\w+)[ ]{{2,}}(?P<law>[\w. \-\(\)]+)".format(action=ACTION)

    def clean(self, matches):
        matches['desc'] = re.sub(r' +', ' ', matches['desc'].strip())
        matches['law'] = re.sub(r' +', ' ', matches['law'].strip())
        return matches

    def is_enabled(self):
        in_offense_section = super().is_enabled()
        return in_offense_section and self.state.offense_num

    def set_state(self, state):
        state.is_desc_ext_possible = True

    def extract(self, matches, report):
        record = {
            "Action": matches["action"],
            "Description": matches["desc"],
            "Severity": matches["severity"],
            "Law": matches["law"],
        }
        offenses = report[self.state.section]
        offenses.current.add_record(record)


class OffenseRecordDescriptionExtended(OffenseSectionParser):
    """
    Extract offense row like:
        CHARGED  SPEEDING  INFRACTION  G.S. 20-141(B)  4450
                   EXTRA INFO ON NEXT LINE
    """

    # pylint: disable=line-too-long
    pattern = r"^\s*(?P<desc_ext>(?:(?!\s+(?:{}|{}|Plea|{}|Disposition\s+Method))\s+\S+)+)".format(ACTION, SEVERITY, GARBAGE_TEXT)

    def is_enabled(self):
        in_offense_section = super().is_enabled()
        return in_offense_section and self.state.is_desc_ext_possible

    def clean(self, matches):
        matches["desc_ext"] = re.sub(r' +', ' ', matches["desc_ext"].strip())
        return matches

    def extract(self, matches, report):
        offenses = report[self.state.section]
        record = offenses.current.current_record()
        record['Description'] =  f"{record['Description']} {matches['desc_ext']}"


class OffenseDisposedDate(OffenseSectionParser):

    pattern = r".*Disposed\s+on:\s*(?P<value>[\d/:]+)"
    section = ("Offense Record", "Disposed On")

    def set_state(self, state):
        state.is_desc_ext_possible = False

    def clean(self, matches):
        """Parse and convert the date to ISO 8601 format"""
        date = dt.datetime.strptime(matches["value"], "%m/%d/%Y").date()
        matches["value"] = date.isoformat()
        return matches

    def extract(self, matches, report):
        offenses = report[self.state.section]
        offenses.current["Disposed On"] = matches["value"]


class OffenseDispositionMethod(OffenseSectionParser):

    pattern = r"\s*Disposition Method:\s*(?P<value>[\w\- ]+)"
    section = ("Offense Record", "Disposition Method")

    def clean(self, matches):
        matches['value'] = re.sub(r' +', ' ', matches['value'].strip())
        return matches

    def set_state(self, state):
        """Since Disposition is the last field in an offense, reset offense_num."""
        state.offense_num = 0
        state.is_desc_ext_possible = False

    def extract(self, matches, report):
        offenses = report[self.state.section]
        offenses.current["Disposition Method"] = matches["value"]


class OffensePlea(OffenseSectionParser):
    pattern = r"\s*Plea:\s*(?P<value>[\w ]+)Verdict:"
    section = ("Offense Record", "Plea")

    def clean(self, matches):
        matches['value'] = re.sub(r' +', ' ', matches['value'].strip())
        return matches

    def set_state(self, state):
        state.is_desc_ext_possible = False

    def extract(self, matches, report):
        offenses = report[self.state.section]
        offenses.current["Plea"] = matches["value"]


class OffenseVerdict(OffenseSectionParser):
    pattern = r"\s*.*Verdict:\s*(?P<value>[\w ]+)Disposed\s*on:"
    section = ("Offense Record", "Verdict")

    def clean(self, matches):
        matches['value'] = re.sub(r' +', ' ', matches['value'].strip())
        return matches

    def set_state(self, state):
        state.is_desc_ext_possible = False

    def extract(self, matches, report):
        offenses = report[self.state.section]
        offenses.current["Verdict"] = matches["value"]
