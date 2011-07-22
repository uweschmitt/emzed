
class PeakMap(object):

    def __init__(self, specs = []):
        self.specs = specs

    def __len__(self):
        return len(self.specs)


    def __iter__(self):
        return iter(self.specs)

    def filter(self, predicate):

        return PeakMap( [ s for s in self.specs if predicate(s) ] )
