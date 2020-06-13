"""Parsing classes to extract text from CIPRS Detailed PDF"""

import datetime as dt
import logging
import re

from ciprs import DISPOSITION_CODES
from ciprs.parser.base import Parser
from ciprs.const import Section

logger = logging.getLogger(__name__)


class CaseDetails(Parser):
    """Extract County and File No from header on top of first page"""

    pattern = (
        r"\s*Case (Details|Summary) for Court Case[\s:]+(?P<county>\w+) (?P<fileno>\w+)"
    )

    def is_enabled(self):
        """Only enabled when in intro header section."""
        return self.state.section == Section.HEADER

    def extract(self, matches, report):
        report["General"]["County"] = matches["county"]
        report["General"]["File No"] = matches["fileno"]


class CaseStatus(Parser):

    pattern = r"\s*Case Status:\s*(?P<value>\w+)"
    section = ("Case Information", "Case Status")


class OffenseRecordRow(Parser):
    """
    Extract offense row like:
        CHARGED  SPEEDING  INFRACTION  G.S. 20-141(B)  4450
    """

    # pylint: disable=line-too-long
    pattern = r"\s*(?P<action>\w+)\s+(?P<desc>[\w \-\(\)]+)[ ]{2,}(?P<severity>\w+)[ ]{2,}(?P<law>[\w. \-\(\)]+)"

    def is_enabled(self):
        return self.state.offense_num and self.state.section in (
            "District Court Offense Information",
        )

    def extract(self, matches, report):
        record = {
            "Action": matches["action"],
            "Description": matches["desc"],
            "Severity": matches["severity"],
            "Law": matches["law"],
        }
        offenses = report[self.state.section]
        offenses.current.add_record(record)


class OffenseRecordRowWithNumber(Parser):
    """
    Extract offense row like:
        54  CHARGED  SPEEDING  INFRACTION  G.S. 20-141(B)
    """

    # pylint: disable=line-too-long
    pattern = r"\s*(?P<num>[\d]+)\s*(?P<action>\w+)[ ]{2,}(?P<desc>[\w \-\(\)]+)[ ]{2,}(?P<severity>\w+)[ ]{2,}(?P<law>[\w. \-\(\)]+)"

    def set_state(self, state):
        # if "num" not in state:
        #     self.report[self.state["section"]].append({"Records": []})
        state.offense_num = self.matches["num"]

    def extract(self, matches, report):
        record = {
            "Action": matches["action"],
            "Description": matches["desc"],
            "Severity": matches["severity"],
            "Law": matches["law"],
        }
        offenses = report[self.state.section]
        offenses.new().add_record(record)
        # report[self.state["section"]].new_offense(record)
        # if not report[self.state["section"]]:
        #     report[self.state["section"]].append({"Records": []})
        # report[self.state["section"]][-1]["Records"].append(record)
        # report["Offense Record"]["Records"].append(record)


class OffenseDisposedDate(Parser):

    pattern = r".*Disposed on:\s*(?P<value>[\d/:]+)"
    section = ("Offense Record", "Disposed On")

    def clean(self, matches):
        """Parse and convert the date to ISO 8601 format"""
        date = dt.datetime.strptime(matches["value"], "%m/%d/%Y").date()
        matches["value"] = date.isoformat()
        return matches

    def extract(self, matches, report):
        offenses = report[self.state.section]
        offenses.current["Disposed On"] = matches["value"]


class CaseWasServedOnDate(Parser):

    pattern = r".*Case Was Served on:\s*(?P<value>[\d/:]+)"
    section = ("Offense Record", "Arrest Date")

    def clean(self, matches):
        """Parse and convert the date to ISO 8601 format"""
        date = dt.datetime.strptime(matches["value"], "%m/%d/%Y").date()
        matches["value"] = date.isoformat()
        return matches


class OffenseDispositionMethod(Parser):

    pattern = r"\s*Disposition Method:\s*(?P<value>[\w ]+)"
    section = ("Offense Record", "Disposition Method")

    def set_state(self, state):
        state.offense_num = 0

    # def clean(self, matches):
    #     """Replace disposition method with ASIC code"""
    #     disposition_method = matches["value"]
    #     matches["value"] = DISPOSITION_CODES.get(disposition_method, disposition_method)
    #     return matches

    def extract(self, matches, report):
        report[self.state.section].add_disposition_method(matches["value"])
        # report[self.state["section"]][-1]["Disposition Method"] = matches["value"]


class OffenseDateTime(Parser):

    pattern = r".*Offense Date/Time:\s*(?P<value>[\w/ :]+[AaPp][Mm])"
    section = ("Case Information", "Offense Date")

    def clean(self, matches):
        """Parse and convert to the date and time in ISO 8601 format"""
        date = dt.datetime.strptime(matches["value"], "%m/%d/%Y %I:%M %p")
        matches["value"] = date.isoformat()
        return matches


class DefendentName(Parser):

    pattern = r"\s*Defendant: \s*(?P<value>[\w,/]+)"
    section = ("Defendant", "Name")

    def clean(self, matches):
        # Change name from last,first,middle to FIRST MIDDLE LAST
        name = matches["value"]
        name_list = name.split(",")
        try:
            if len(name_list) == 2:
                name = "{} {}".format(name_list[1], name_list[0])
            elif len(name_list) == 3:
                name = "{} {} {}".format(name_list[1], name_list[2], name_list[0])
        except:
            name = ""
        matches["value"] = name.upper()
        return matches


class DefendentRace(Parser):

    pattern = r"\s*Race: \s*(?P<value>\w+)"
    section = ("Defendant", "Race")


class DefendentSex(Parser):

    pattern = r"\s*Sex: \s*(?P<value>\w+)"
    section = ("Defendant", "Sex")

    def clean(self, matches):
        """Parse and convert defendent sex to M or F"""
        sex = matches["value"].lower()
        if sex == "female":
            matches["value"] = "F"
        elif sex == "male":
            matches["value"] = "M"
        else:
            matches["value"] = ""
        return matches


class DefendentDOB(Parser):

    pattern = r"\s*Date of Birth/Estimated Age:[\sa-zA-Z]*(?P<value>[\d/]+)[ ]{2,}"
    re_method = "search"
    section = ("Defendant", "Date of Birth/Estimated Age")
    is_line_parser = False

    def clean(self, matches):
        """Parse and convert the date to ISO 8601 format"""
        date = dt.datetime.strptime(matches["value"], "%m/%d/%Y").date()
        matches["value"] = date.isoformat()
        return matches


class DistrictSuperiorCourt(Parser):

    pattern = r".*"  # match anything
    re_method = "search"
    is_line_parser = False

    def clean(self, matches):
        """
        If file number includes "CRS", check Superior.
        If file number includes "CR" but not "CRS", check District.
        If file number does not include "CR" at all, leave blank.
        """
        data = {}
        fileno = self.report["General"].get("File No", "")
        if fileno:
            if "CR" in fileno:
                if "CRS" in fileno:
                    data["Superior"] = "Yes"
                else:
                    data["District"] = "Yes"
        return data

    def extract(self, matches, report):
        report["General"].update(matches)


class OffenseDate(Parser):

    pattern = r".*Offense Date:[\sa-zA-Z]*(?P<value>[\d/]+)[ ]{2,}"
    section = ("Case Information", "Offense Date")

    def clean(self, matches):
        """Parse and convert the date to ISO 8601 format"""
        date = dt.datetime.strptime(matches["value"], "%m/%d/%Y").date()
        matches["value"] = date.isoformat()
        return matches
