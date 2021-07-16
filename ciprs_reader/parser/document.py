from ciprs_reader.parser.base import Parser
from ciprs_reader.const import Section
from lark import Lark, Transformer
import datetime as dt

PARSER = Lark(r"""
    document        : ((offense_section | _IGNORE) | _NEWLINE)*

    _IGNORE.-1      : (/[^\n]/)+
    _ignore_line   : _IGNORE _NEWLINE

    offense_section : jurisdiction (_ignore_line+ offenses |_missing_offenses)
    jurisdiction    : JURISDICTION "Court" "Offense" "Information" _NEWLINE
    _missing_offenses : "This" "case" "does" "not" "have" "a" "record" _IGNORE

    offenses        : offense+
    offense         : offense_line ~ 2 _offense_info disposition_method _NEWLINE

    offense_line    : _RECORD_NUM? action (_some_offense | _no_offense)
    _RECORD_NUM.0   : INT
    action          : ACTION
    _no_offense     : _MINUS+ _NEWLINE

    _some_offense   : description severity law _NEWLINE (description_ext _NEWLINE)*
    description     : (/(?!TRAFFIC|INFRACTION|MISDEMEANOR|FELONY)\S+/)+
    severity        : SEVERITY
    law             : LAW_PRE TEXT+
    description_ext : (/(?!Plea:|CONVICTED)\S+/)+

    _offense_info   : "Plea:" plea "Verdict:" verdict "Disposed" "on:" disposed_on _NEWLINE
    plea            : (/(?!Verdict:)\S+/)+ | _MINUS
    verdict         : (/(?!Disposed)\S+/)+ | _MINUS
    disposed_on     : TEXT+ | _MINUS

    disposition_method : "Disposition" "Method:" TEXT+

    JURISDICTION    : "District" | "DISTRICT"
                    | "Superior" | "SUPERIOR"

    ACTION  : "CHARGED"
            | "CONVICTED"
            | "ARRAIGNED"

    SEVERITY    : "TRAFFIC"
                | "INFRACTION"
                | "MISDEMEANOR"
                | "FELONY"

    LAW_PRE     : "G.S."
    TEXT.0      : /\S+/
    _MINUS.0    : "-"

    _NEWLINE    : /[\r\n]/+
    WS_INLINE   : (" "|/\t/|/\f/)+

    %import common.INT
    %ignore WS_INLINE
""", start='document', parser='lalr')

def key_string_tuple(key):
    return lambda self, str_list: (key, " ".join(str_list))

list_to_string = lambda self, str_list: " ".join(str_list)

class MyTransformer(Transformer):
    def disposed_on(self, items):
        value = " ".join(items)
        date = dt.datetime.strptime(value, "%m/%d/%Y").date()
        return date.isoformat()
    def offense_line(self, items):
        # extract description_extended (if it exists) and combine with descritpion
        # action description severity law description_ext?
        (*fields, last_field) = items
        offense_line_dict = dict(fields)
        (key, value) = last_field
        if key == 'Description Extended':
            offense_line_dict['Description'] = " ".join([offense_line_dict['Description'], value])
        else:
            offense_line_dict[key] = value
        return offense_line_dict
    def offense_section(self, items):
        if not items:
            return None
        if len(items) < 2:
            return items[0], []
        return items[0], items[1]
    def offense(self, items):
        offense_dict = {
            'Records': [items[0]],
            'Disposed On': items[4],
            'Disposition Method': items[5],
        }
        if items[1] and 'Description' in items[1] and items[1]['Description']:
            offense_dict['Records'].append(items[1])
        if items[2]:
            offense_dict['Plea'] = items[2]
        if items[3]:
            offense_dict['Verdict'] = items[3]
        return offense_dict

    document = dict
    offenses = list

    action = key_string_tuple("Action")
    description = key_string_tuple("Description")
    law = key_string_tuple("Law")
    severity = key_string_tuple("Severity")
    description_ext = key_string_tuple("Description Extended")

    # some of these should probably just be `str`
    # need to figure out how to get lark to store those as a string instead of list of strings
    jurisdiction = list_to_string
    disposition_method = list_to_string
    plea = list_to_string
    verdict = list_to_string

    JURISDICTION = str
    ACTION = str
    SEVERITY = str
    TEXT = str
    LAW_PRE = str


class OffenseSectionParser:
    """Only enabled when in offense-related sections."""

    def __init__(self, report, state):
        self.state = state
        self.report = report

    def find(self, document):
        tree = PARSER.parse(document)
        data = MyTransformer().transform(tree)
        self.extract(data)

    def extract(self, raw_data):
        if 'District' in raw_data:
            self.report['District Court Offense Information'] = raw_data['District']
        if 'Superior' in raw_data:
            self.report['Superior Court Offense Information'] = raw_data['Superior']
