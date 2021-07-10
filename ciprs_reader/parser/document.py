from ciprs_reader.parser.base import Parser
from ciprs_reader.const import Section
from ciprs_reader.parser.section.offense import OFFENSE_SECTION_PARSERS
from lark import Lark, Transformer
import pprint

class MyTransformer(Transformer):
    def jurisdiction(self, items):
        return " ".join(items)
    def record_num(self, item):
        (num,) = item
        return "Record Number", int(num)
    def action(self, item):
        (action,) = item
        return "Action", str(action)
    def description(self, items):
        return "Description", " ".join(items)
    def description_ext(self, items):
        return "Description Extended", " ".join(items)
    def severity(self, item):
        (severity,) = item if item else ("",)
        return "Severity", str(severity)
    def law(self, item):
        (law_string,) = item if item else ("",)
        # convert multiple spaces within law into single spaces
        law = ' '.join(law_string.split())
        return "Law", str(law)
    def disposition_method(self, items):
        return " ".join(items)
    def plea(self, items):
        return " ".join(items)
    def verdict(self, items):
        return " ".join(items)
    def disposed_on(self, items):
        return " ".join(items)
    def offense_section(self, items):
        if not items:
            return None
        return items[0], items[1]
    def offense(self, items):
        return {
            'Lines': [items[0], items[1]],
            'Plea': items[2],
            'Verdict': items[3],
            'Disposed On': items[4],
            'Disposition Method': items[5],
        }

    document = dict
    offenses = list
    offense_line = dict


class OffenseSectionParser:
    """Only enabled when in offense-related sections."""

    def __init__(self, report, state):
        self.state = state
        self.parser = Lark(r"""
            document        : (offense_section | _ignore | _IGNORE+)*

            _ignore         : _IGNORE+ _NEWLINE

            offense_section : jurisdiction _ignore? _ignore offenses

            jurisdiction    : WORD ~ 2 "Offense" "Information" _NEWLINE

            offenses        : offense+
            offense         : offense_line ~ 2 _offense_info disposition_method _NEWLINE

            _offense_info   : "Plea:" plea "Verdict:" verdict "Disposed" "on:" disposed_on _NEWLINE
            plea            : WORD+ | "-"
            verdict         : WORD+ | "-"
            disposed_on     : TEXT+ | "-"

            disposition_method  : "Disposition" "Method:" TEXT+

            offense_line    : record_num? action description severity law _NEWLINE (description_ext _NEWLINE)*
            record_num      : INT
            action          : ACTION
            description     : TEXT+ | "-"
            severity        : SEVERITY | "-"
            law             : /\S[\S ]+\S/ | "-"
            description_ext : (/(?!(?:Plea:|CONVICTED))\S+/)+

            ACTION  : "CHARGED"
                    | "CONVICTED"
                    | "ARRAIGNED"

            SEVERITY    : "TRAFFIC"
                        | "INFRACTION"
                        | "MISDEMEANOR"
                        | "FELONY"

            TEXT        : /\S+/
            _IGNORE     : TEXT | /\f/
            _NEWLINE    : NEWLINE
            _EOL        : /\f/

            %import common.INT
            %import common.WORD
            %import common.WS_INLINE
            %import common.NEWLINE
            %ignore WS_INLINE
        """, start='document')

    def find(self, document):
        tree = self.parser.parse(document)
        print(tree.pretty())
        stuff = MyTransformer().transform(tree)
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(stuff)
