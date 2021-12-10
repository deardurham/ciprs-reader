import datetime as dt
import re

from ciprs_reader.const import Section
from ciprs_reader.parser.base import Parser

NUM = r"\d+"
ACTION = r"(?:ARRAIGNED|CHARGED|CONVICTED)"
SEVERITY = r"(?:MISDEMEANOR|TRAFFIC|INFRACTION|FELONY)"
DESC = r"(?:[\S ])+?"
LAW = r"[\w. \-\(\)]+"
DESC_EXT = r"(?:(?!\s+({}|{}|Plea))\s+\S+)*".format(ACTION, SEVERITY)

class OffenseRecordRowWithNumber(Parser):
    """
    Extract offense row like:
        54  CHARGED  SPEEDING  INFRACTION  G.S. 20-141(B)
    """

    pattern = r"^\s+(?P<num>{})\s+(?P<action>{})\s+(?P<desc>{})\s+(?P<severity>{})\s+(?P<law>{})(?P<desc_ext>{})".format(NUM, ACTION, DESC, SEVERITY, LAW, DESC_EXT)

    def set_state(self, state):
        """
        Set offense_num so other parsers, like OffenseRecordRow,
        can use it.
        """
        state.offense_num = self.matches[0]["num"]

    def get_record(self, matches):
        description_strings = [
            re.sub(r' +', ' ', matches["desc"].strip()),
        ]
        if matches["desc_ext"]:
            description_strings.append(re.sub(r' +', ' ', matches["desc_ext"].strip()))

        return {
            "Action": matches["action"],
            "Description": " ".join(description_strings),
            "Severity": matches["severity"],
            "Law": re.sub(r' +', ' ', matches["law"].strip()),
        }

    def extract(self, matches, report):
        offenses = report[self.state.section]
        # Whenever a row with number is encountered, it indicates a new
        # offense record, so we always add a NEW offense below.
        for match in matches:
            record = self.get_record(match)
            offenses.new().add_record(record)


class OffenseRecordRow(Parser):
    """
    Extract offense row like:
        CHARGED  SPEEDING  INFRACTION  G.S. 20-141(B)  4450
    """

    #pattern = r"^\s+(?P<action>(?:ARRAIGNED|CHARGED|CONVICTED))\s+(?P<desc>[\S ]+)\s+(?P<severity>(MISDEMEANOR|TRAFFIC|INFRACTION|FELONY))\s+(?P<law>[\w. \-\(\)]+)(?P<desc_ext>(?:(?!\s+Plea)\s*.+?)*)"
    pattern = r"^\s+(?P<action>{})\s+(?P<desc>{})\s+(?P<severity>{})\s+(?P<law>{})(?P<desc_ext>{})".format(ACTION, DESC, SEVERITY, LAW, DESC_EXT)

    def is_enabled(self):
        in_offense_section = super().is_enabled()
        return in_offense_section and self.state.offense_num

    def get_record(self, matches):
        description_strings = [
            re.sub(r' +', ' ', matches["desc"].strip()),
        ]
        if matches["desc_ext"]:
            description_strings.append(re.sub(r' +', ' ', matches["desc_ext"].strip()))

        return {
            "Action": matches["action"],
            "Description": " ".join(description_strings),
            "Severity": matches["severity"],
            "Law": re.sub(r' +', ' ', matches["law"].strip()),
        }

    def extract(self, matches, report):
        offenses = report[self.state.section]
        for match in matches:
            record = self.get_record(match)
            offenses.current.add_record(record)


class OffenseDisposedDate(Parser):

    pattern = r"^.*Disposed\s*on:\s*(?P<value>[\d/:]+)"
    section = ("Offense Record", "Disposed On")

    def clean(self, matches):
        """Parse and convert the date to ISO 8601 format"""
        date = dt.datetime.strptime(matches["value"], "%m/%d/%Y").date()
        matches["value"] = date.isoformat()
        return matches

    def extract(self, matches, report):
        offenses = report[self.state.section]
        offenses.current["Disposed On"] = matches[0]["value"]


class OffenseDispositionMethod(Parser):

    pattern = r"^.*?Disposition\s+Method:\s*(?P<value>[\w\- ]+)\s*$"
    section = ("Offense Record", "Disposition Method")

    def set_state(self, state):
        """Since Disposition is the last field in an offense, reset offense_num."""
        state.offense_num = 0

    def extract(self, matches, report):
        offenses = report[self.state.section]
        offenses.current["Disposition Method"] = re.sub(r" +", " ", matches[0]["value"].strip())


class OffensePlea(Parser):
    pattern = r"^.*?Plea:\s*(?P<value>[\w ]+?)\s*Verdict:"
    section = ("Offense Record", "Plea")

    def extract(self, matches, report):
        offenses = report[self.state.section]
        offenses.current["Plea"] = matches[0]["value"]


class OffenseVerdict(Parser):
    pattern = r"^.*Verdict:\s*(?P<value>[\w ]+?)\s*Disposed"
    section = ("Offense Record", "Verdict")

    def extract(self, matches, report):
        offenses = report[self.state.section]
        offenses.current["Verdict"] = re.sub(r" +", " ", matches[0]["value"].strip())


OFFENSE_SECTION_PARSERS = (
    # Section: Offenses (District & Superior)
    OffenseRecordRowWithNumber,
    OffenseRecordRow,
    OffenseDisposedDate,
    OffenseDispositionMethod,
    OffensePlea,
    OffenseVerdict,
)
