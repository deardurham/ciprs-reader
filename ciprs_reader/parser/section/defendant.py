from ciprs_reader.const import Section
from ciprs_reader.parser.base import Parser


class DefendantParser(Parser):
    """Only enabled when in Defendant section."""

    def is_enabled(self):
        return self.state.section == Section.DEFENDANT


class DefendantRace(DefendantParser):

    pattern = [r"\s*Race:", r"(?P<value>\w+)"]
    section = ("Defendant", "Race")


class DefendantSex(DefendantParser):

    pattern = [r"\s*Sex:", r"(?P<value>\w+)"]
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
