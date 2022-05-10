"""Parsing classes to extract text from CIPRS Detailed PDF"""

import logging
import re

logger = logging.getLogger(__name__)


class Parser:
    """Base parsing object to search and extract data into report"""

    # Regular expression search pattern
    pattern = None
    re_method = "match"
    # Default location in report to save match, expressed as tuple
    # For example:
    #   ("Case Information", "Case Status")
    #   will save to:
    #   report['Case Information']['Case Status']
    section = []
    is_line_parser = True

    def __init__(self, report, state):
        if isinstance(self.pattern, list):
            pattern = r"\s*".join(self.pattern)
        elif isinstance(self.pattern, str):
            pattern = self.pattern
        else:
            raise TypeError('Pattern must be string or array')
        self.re = re.compile(pattern)
        self.report = report
        self.matches = None
        self.document = None
        name = f"{__name__}.{self.__class__.__name__}"
        self.logger = logging.getLogger(name)
        self.state = state

    def match(self, document):
        """Search for match in document"""
        self.matches = None
        self.document = document
        if self.re_method == "match":
            matches = self.re.match(str(document))
        else:
            matches = self.re.search(str(document))
        if matches:
            matches = matches.groupdict()
            # strip whitespace on any values
            for key, val in matches.items():
                matches[key] = val.strip()
            if self.is_line_parser:
                self.logger.info("Matched: %s in %s", matches, str(document).strip())
            else:
                self.logger.info("Matched: %s in (document)", matches)
            self.matches = self.clean(matches)
        else:
            if self.is_line_parser:
                self.logger.debug("No match: %s", str(document).strip())
            else:
                self.logger.debug("No match: (document)")
        return self.matches

    def clean(self, matches):
        """Overridable hook to clean matches"""
        return matches

    def is_enabled(self):
        """
        Parsers only run when enabled. Override this method to
        toggle is_enabled based on parser state.
        """
        return True

    def set_state(self, state):
        pass

    def find(self, document):
        """Look for match and run extract() if found"""
        if not self.is_enabled():
            return
        self.match(document)
        if self.matches:
            self.extract(self.matches, self.report)
            self.set_state(self.state)
            # pylint: disable=logging-fstring-interpolation
            self.logger.info(f"State: {self.state}")

    def extract(self, matches, report):
        """
        Update report with match, defaulting to a named match "value".
        Override this function for more specific actions.
        """
        report[self.section[0]][self.section[1]] = matches["value"]
