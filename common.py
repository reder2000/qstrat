from pandas import Timestamp

Date = Timestamp


class indexing_dict:
    def __init__(self):
        self.d = {}

    def __getitem__(self, v):
        if not v in self.d:
            self.d[v] = len(self.d)
        return self.d[v]

    def __contains__(self, v):
        return v in self.d
