import datetime as dt

from ciprs_reader.const import Section
from ciprs_reader.parser.base import Parser


class CaseInformationParser(Parser):
    """Only enabled when in Case Information section."""

    def is_enabled(self):
        return self.state.section == Section.CASE_INFORMATION


class CaseStatus(CaseInformationParser):

    pattern = [r"\s*Case", "Status:", r"(?P<value>\w+)"]
    section = ("Case Information", "Case Status")


class OffenseDate(CaseInformationParser):

    pattern = [r"\s*Offense", r"Date:[\sa-zA-Z]*(?P<value>[\d/]+)[ ]{2,}"]
    section = ("Case Information", "Offense Date")

    def clean(self, matches):
        """Parse and convert the date to ISO 8601 format"""
        date = dt.datetime.strptime(matches["value"], "%m/%d/%Y")
        matches["value"] = date.isoformat()
        return matches


class OffenseDateTime(CaseInformationParser):

    pattern = [r"\s*Offense", r"Date/Time:\s*(?P<value>[\w/ :]+[AaPp][Mm])"]
    section = ("Case Information", "Offense Date")

    def clean(self, matches):
        """Parse and convert to the date and time in ISO 8601 format"""
        date = dt.datetime.strptime(matches["value"], "%m/%d/%Y %I:%M %p")
        matches["value"] = date.isoformat()
        return matches


class CaseWasServedOnDate(CaseInformationParser):

    pattern = ["Case", "Was", "Served", r"on:\s*(?P<value>[\d/:]+)"]
    re_method = "search"
    section = ("Case Information", "Arrest Date")

    def clean(self, matches):
        """Parse and convert the date to ISO 8601 format"""
        date = dt.datetime.strptime(matches["value"], "%m/%d/%Y").date()
        matches["value"] = date.isoformat()
        return matches
