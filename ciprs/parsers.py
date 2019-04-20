"""Parsing classes to extract text from CIPRS Detailed PDF"""

import re


class Parser:
    """Base parsing object to search and extract data into report"""

    # Regular expression search pattern
    pattern = None
    # Default location in report to save match, expressed as tuple
    # For example:
    #   ("Case Information", "Case Status")
    #   will save to:
    #   report['Case Information']['Case Status']
    section = []

    def __init__(self, report=None):
        self.re = re.compile(self.pattern)
        self.report = report
        self.matches = None
        self.document = None

    def match(self, document):
        """Search for match in document"""
        self.matches = None
        self.document = document
        matches = self.re.match(str(document))
        if matches:
            self.matches = matches.groupdict()
            # strip whitespace on any values
            for key, val in self.matches.items():
                self.matches[key] = val.strip()
        return self.matches

    def find(self, document):
        """Look for match and run extract() if found"""
        self.match(document)
        if self.matches:
            self.extract(self.matches, self.report)

    def extract(self, matches, report):
        """
        Update report with match, defaulting to a named match "value".
        Override this function for more specific actions.
        """
        report[self.section[0]][self.section[1]] = matches["value"]


class CaseDetails(Parser):
    """Extract County and File No from header on top of first page"""

    pattern = r"\s*Case Details for Court Case (?P<county>\w+) (?P<fileno>\w+)"

    def extract(self, matches, report):
        report['General']['County'] = matches['county']
        report['General']['File No'] = matches['fileno']


class CaseStatus(Parser):

    pattern = r"\s*Case Status:\s*(?P<value>\w+)"
    section = ("Case Information", "Case Status")


class OffenseRecordRow(Parser):
    """
    Extract offense row like:
        CHARGED  SPEEDING  INFRACTION  G.S. 20-141(B)  4450
    """

    # pylint: disable=line-too-long
    pattern = r"\s*(?P<action>\w+)\s+(?P<desc>[\w \-\(\)]+)[ ]{2,}(?P<severity>\w+)[ ]{2,}(?P<law>[\w. \-\(\)]+)[ ]{2,}(?P<code>\d+)"

    def extract(self, matches, report):
        record = {
            'Action': matches['action'],
            'Description': matches['desc'],
            'Severity': matches['severity'],
            'Law': matches['law'],
            'Code': matches['code'],
        }
        report['Offense Record']['Records'].append(record)
