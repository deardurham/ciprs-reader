import datetime as dt
import re

from ciprs_reader.const import Section
from ciprs_reader.parser.base import Parser


class OffenseRecordRowWithNumber(Parser):
    """
    Extract offense row like:
        54  CHARGED  SPEEDING  INFRACTION  G.S. 20-141(B)
    """

    # pylint: disable=line-too-long
    #pattern = r"^\s*(?P<num>[\d]+)\s*(?P<action>CHARGED)\s*(?P<desc>.+)\s*(?P<severity>.+)\s*(?P<law>.+)(?P<desc_ext>(?:(?!\s*CONVICTED)\s*.+)*)"
    pattern = r"^.*?(?P<num>[\d]+)\s+CHARGED\s+(?P<desc>[\S ]+)\s+(?P<severity>(MISDEMEANOR|TRAFFIC|INFRACTION))\s+(?P<law>[\w. \-\(\)]+)(?P<desc_ext>(?:(?!\s+CONVICTED)\s*.+?)*)"

    def set_state(self, state):
        """
        Set offense_num so other parsers, like OffenseRecordRow,
        can use it.
        """
        state.offense_num = self.matches["num"]

    def extract(self, matches, report):
        record = {
            "Action": "CHARGED",
            "Description": re.sub(' +', ' ', matches["desc"].strip()),
            "Severity": matches["severity"].strip(),
            "Law": matches["law"].strip(),
            "Description_extended": matches["desc_ext"].strip(),
        }
        offenses = report[self.state.section]
        # Whenever a row with number is encountered, it indicates a new
        # offense record, so we always add a NEW offense below.
        offenses.new().add_record(record)


class OffenseRecordRow(Parser):
    """
    Extract offense row like:
        CHARGED  SPEEDING  INFRACTION  G.S. 20-141(B)  4450
    """

    # pylint: disable=line-too-long
    pattern = r"^\s*(?P<num>[\d]+)\s*(?P<action>CHARGED)\s*(?P<desc>.+)\s*(?P<severity>.+)\s*(?P<law>.+)(?P<desc_ext>(?:(?!\s*Plea)\s*.+)*)"

    def is_enabled(self):
        in_offense_section = super().is_enabled()
        return in_offense_section and self.state.offense_num

    def extract(self, matches, report):
        record = {
            "Action": matches["action"],
            "Description": matches["desc"],
            "Severity": matches["severity"],
            "Law": matches["law"],
        }
        offenses = report[self.state.section]
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
        offenses.current["Disposed On"] = matches["value"]


class OffenseDispositionMethod(Parser):

    pattern = r"^\s*Disposition\s*Method:\s*(?P<value>[\w\- ]+)"
    section = ("Offense Record", "Disposition Method")

    def set_state(self, state):
        """Since Disposition is the last field in an offense, reset offense_num."""
        state.offense_num = 0

    def extract(self, matches, report):
        offenses = report[self.state.section]
        offenses.current["Disposition Method"] = matches["value"]


class OffensePlea(Parser):
    pattern = r"^\s*Plea:\s*(?P<value>.+?)\s*Verdict:"
    section = ("Offense Record", "Plea")

    def extract(self, matches, report):
        offenses = report[self.state.section]
        offenses.current["Plea"] = matches["value"]


class OffenseVerdict(Parser):
    pattern = r"^.*Verdict:\s*(?P<value>.+?)\s*Disposed"
    section = ("Offense Record", "Verdict")

    def extract(self, matches, report):
        offenses = report[self.state.section]
        offenses.current["Verdict"] = matches["value"]


OFFENSE_SECTION_PARSERS = (
    # Section: Offenses (District & Superior)
    OffenseRecordRow,
    OffenseRecordRowWithNumber,
    OffenseDisposedDate,
    OffenseDispositionMethod,
    OffensePlea,
    OffenseVerdict,
)
