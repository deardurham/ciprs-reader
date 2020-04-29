import collections


class Court(collections.UserList):
    def add_record(self, record):
        offense = Offense()
        offense.add_record(record)
        self.data.append(offense)

    def add_disposition_method(self, method):
        self.data[-1]["Disposition Method"] = method

    def __json__(self):
        return self.data


class Offense(collections.UserDict):
    def add_record(self, record):
        if "records" not in self.data:
            self.data["records"] = []
        self.data["records"].append(record)

    def __json__(self):
        return self.data
