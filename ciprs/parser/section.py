from .base import Parser


class Section(Parser):
    def set_state(self, state):
        state["section"] = self.matches

    def extract(self, matches, report):
        pass


class CaseInformation(Section):

    pattern = r"^\s*Case Information\s*$"

    def clean(self, matches):
        return "Case Information"


class DistrictCourtOffenseSection(Section):

    pattern = r"^\s*District Court Offense Information\s*$"

    def clean(self, matches):
        return "District Court Offense Information"
