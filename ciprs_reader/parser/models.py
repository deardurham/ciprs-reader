import collections


class Offenses(collections.UserList):
    """
    Simple list wrapper to manage Offense objects more easily and
    is still easily JSON serializable.
    """

    @property
    def current(self):
        if not self.data:
            self.new()
        return self.data[-1]

    def new(self):
        self.data.append(Offense())
        return self.current

    def __json__(self):
        return self.data


class Offense(collections.UserDict):
    """
    Offense wrapper to easily add new records and is still easily
    JSON serializable.
    """

    def add_record(self, record):
        if "Records" not in self.data:
            self.data["Records"] = []
        self.data["Records"].append(record)

    def __json__(self):
        return self.data
