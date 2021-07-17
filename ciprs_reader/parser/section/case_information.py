from ciprs_reader.const import Section
from ciprs_reader.parser import utils
from ciprs_reader.parser.base import Parser


class CaseInformationParser(Parser):
    """Only enabled when in Case Information section."""

    def is_enabled(self):
        return self.state.section == Section.CASE_INFORMATION


class CaseStatus(CaseInformationParser):

    pattern = r"\s*Case Status:\s*(?P<value>\w+)"
    section = ("Case Information", "Case Status")


class OffenseDate(CaseInformationParser):

    pattern = r".*Offense Date:[\sa-zA-Z]*(?P<value>[\d/]+)[ ]{2,}"
    section = ("Case Information", "Offense Date")

    def clean(self, matches):
        """Parse and convert the date to ISO 8601 format"""
        matches["value"] = utils.parse_date_isoformat(matches["value"], "%m/%d/%Y", include_time=True)
        return matches


class OffenseDateTime(CaseInformationParser):

    pattern = r".*Offense Date/Time:\s*(?P<value>[\w/ :]+[AaPp][Mm])"
    section = ("Case Information", "Offense Date")

    def clean(self, matches):
        """Parse and convert to the date and time in ISO 8601 format"""
        matches["value"] = utils.parse_date_isoformat(matches["value"], "%m/%d/%Y %I:%M %p", include_time=True)
        return matches


class CaseWasServedOnDate(CaseInformationParser):

    pattern = r".*Case Was Served on:\s*(?P<value>[\d/:]+)"
    section = ("Case Information", "Arrest Date")

    def clean(self, matches):
        """Parse and convert the date to ISO 8601 format"""
        matches["value"] = utils.parse_date_isoformat(matches["value"], "%m/%d/%Y")
        return matches
