"""Parsing classes to extract text from CIPRS Detailed PDF"""

import datetime as dt
import logging

from ciprs_reader.parser.base import Parser

logger = logging.getLogger(__name__)


class DefendentDOB(Parser):

    pattern = ["Date", 'of', 'Birth/Estimated', r"Age:[\sa-zA-Z]*(?P<value>[\d/]+)[ ]{2,}"]
    re_method = "search"
    section = ("Defendant", "Date of Birth/Estimated Age")

    def clean(self, matches):
        """Parse and convert the date to ISO 8601 format"""
        try:
            date = dt.datetime.strptime(matches["value"], "%m/%d/%Y").date()
        except ValueError:
            return None
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
            if "CRS" in fileno:
                data["Superior"] = "Yes"
            elif "CR" in fileno or "IF" in fileno:
                data["District"] = "Yes"
        return data

    def extract(self, matches, report):
        report["General"].update(matches)
