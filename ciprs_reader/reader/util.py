"""Utilities for PDFToTextReader"""


def json_default(obj):
    """Helper function to JSON serialize objects when using dumps()."""
    try:
        return obj.__json__()
    except AttributeError:
        raise TypeError("{} can not be JSON encoded".format(type(obj)))


class Reader:
    """Wrapper class to iterate over lines in a string."""

    def __init__(self, source):
        self.source = source
        self.lines = iter(source.splitlines())
        self.current = None

    def next(self):
        self.current = next(self.lines, None)
        return self.current

    def __str__(self):
        return self.current or ""
