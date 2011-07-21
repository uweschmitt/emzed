
class PeakMap(object):

    def __init__(self, specs = None):
        self.specs = specs

    def __len__(self):
        return len(self.specs)


    def __iter__(self):
        return iter(self.specs)
