"""Parsing classes to extract text from CIPRS Detailed PDF"""

import datetime as dt
import re


class Parser:
    """Base parsing object to search and extract data into report"""

    # Regular expression search pattern
    pattern = None
    re_method = 'match'
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
        if self.re_method == 'match':
            matches = self.re.match(str(document))
        else:
            matches = self.re.search(str(document))
        if matches:
            matches = matches.groupdict()
            # strip whitespace on any values
            for key, val in matches.items():
                matches[key] = val.strip()
            self.matches = self.clean(matches)
        return self.matches

    def clean(self, matches):
        """Overridable hook to clean matches"""
        return matches

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


class OffenseDisposedDate(Parser):

    pattern = r"\s*Disposed on:\s*(?P<value>[\d/:]+)"
    section = ("Offense Record", "Disposed On")

    def clean(self, matches):
        """Parse and convert the date to ISO 8601 format"""
        date = dt.datetime.strptime(matches['value'], '%m/%d/%Y').date()
        matches['value'] = date.isoformat()
        return matches


class OffenseDispositionMethod(Parser):

    pattern = r"\s*Disposition Method:\s*(?P<value>[\w ]+)[ ]{2,}"
    section = ("Offense Record", "Disposition Method")


class OffenseDateTime(Parser):

    pattern = r"\s*Offense Date/Time:\s*(?P<value>[\w/ :]+[AaPp][Mm])"
    section = ("Case Information", "Offense Date")

    def clean(self, matches):
        """Parse and convert to the date and time in ISO 8601 format"""
        date = dt.datetime.strptime(matches['value'], '%m/%d/%Y %I:%M %p')
        matches['value'] = date.isoformat()
        return matches


class DefendentName(Parser):

    pattern = r"\s*Defendant: \s*(?P<value>[\w,/]+)"
    section = ("Defendant", "Name")

    def clean(self,matches):
        #Change name from last,first,middle to FIRST MIDDLE LAST
        name = matches['value']
        name_list = name.split(',') 
        name = "{} {} {}".format(name_list[1], name_list[2], name_list[0])
        matches['value'] = name.upper()
        return matches


class DefendentRace(Parser):

    pattern = r"\s*Race: \s*(?P<value>\w+)"
    section = ("Defendant", "Race")


class DefendentSex(Parser):

    pattern = r"\s*Sex: \s*(?P<value>\w+)"
    section = ("Defendant", "Sex")


class DefendentDOB(Parser):

    pattern = r"\s*Date of Birth/Estimated Age:[\sa-zA-Z]*(?P<value>[\d/]+)[ ]{2,}"
    re_method = 'search'
    section = ("Defendant", "Date of Birth/Estimated Age")

    def match(self, document):
        """DOB is split across two lines so the entire document is searched"""
        from ciprs.reader import Reader
        if isinstance(document, Reader):
            return super().match(document.source)
        return super().match(document)

    def clean(self, matches):
        """Parse and convert the date to ISO 8601 format"""
        date = dt.datetime.strptime(matches['value'], '%m/%d/%Y').date()
        matches['value'] = date.isoformat()
        return matches
