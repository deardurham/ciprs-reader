from ciprs_reader.const import Section
from ciprs_reader.parser import utils
from ciprs_reader.parser.base import Parser


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
    pattern = r"\s*(?P<num>[\d]+)\s*(?P<action>\w+)\s+(?P<desc>.+)[ ]{2,}(?P<severity>\w+)[ ]{2,}(?P<law>[\w. \-\(\)]+)"

    def set_state(self, state):
        """
        Set offense_num so other parsers, like OffenseRecordRow,
        can use it.
        """
        state.offense_num = self.matches["num"]

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
    pattern = r"\s*(?P<action>\w+)\s+(?P<desc>.+)[ ]{2,}(?P<severity>\w+)[ ]{2,}(?P<law>[\w. \-\(\)]+)"

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


class OffenseDisposedDate(OffenseSectionParser):

    pattern = r".*Disposed on:\s*(?P<value>[\d/:]+)"
    section = ("Offense Record", "Disposed On")

    def clean(self, matches):
        """Parse and convert the date to ISO 8601 format"""
        matches["value"] = utils.parse_date_isoformat(matches["value"], "%m/%d/%Y")
        return matches

    def extract(self, matches, report):
        offenses = report[self.state.section]
        offenses.current["Disposed On"] = matches["value"]


class OffenseDispositionMethod(OffenseSectionParser):

    pattern = r"\s*Disposition Method:\s*(?P<value>[\w\- ]+)"
    section = ("Offense Record", "Disposition Method")

    def set_state(self, state):
        """Since Disposition is the last field in an offense, reset offense_num."""
        state.offense_num = 0

    def extract(self, matches, report):
        offenses = report[self.state.section]
        offenses.current["Disposition Method"] = matches["value"]


class OffensePlea(OffenseSectionParser):
    pattern = r"\s*Plea:\s*(?P<value>[\w ]+)Verdict:"
    section = ("Offense Record", "Plea")

    def extract(self, matches, report):
        offenses = report[self.state.section]
        offenses.current["Plea"] = matches["value"]


class OffenseVerdict(OffenseSectionParser):
    pattern = r".*Verdict:\s*(?P<value>[\w ]+)Disposed on:"
    section = ("Offense Record", "Verdict")

    def extract(self, matches, report):
        offenses = report[self.state.section]
        offenses.current["Verdict"] = matches["value"]
