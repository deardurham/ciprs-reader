"""Parsing classes to extract text from CIPRS Detailed PDF"""

import logging

from ciprs_reader.parser import utils
from ciprs_reader.parser.base import Parser

logger = logging.getLogger(__name__)


class DefendentDOB(Parser):

    pattern = r"\s*Date of Birth/Estimated Age:[\sa-zA-Z]*(?P<value>[\d/]+)[ ]{2,}"
    re_method = "search"
    section = ("Defendant", "Date of Birth/Estimated Age")
    is_line_parser = False

    def clean(self, matches):
        """Parse and convert the date to ISO 8601 format"""
        matches["value"] = utils.parse_date_isoformat(matches["value"], "%m/%d/%Y")
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
