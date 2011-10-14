import numpy as np

class PeakMap(object):

    def __init__(self, specs = None, meta = None):
        self.specs = [] if specs is None else specs
        self.meta  = dict() if meta is None else meta

    def __len__(self):
        return len(self.specs)


    def __iter__(self):
        return iter(self.specs)

    def filter(self, predicate):

        return PeakMap( [ s for s in self.specs if predicate(s) ], self.meta )

    def removeZeroIntensities(self):
        for spec in self.specs:
            spec.removeZeroIntensities()
        return self

    def sortByMz(self):
        for spec in self.specs:
            spec.sortByMz()
        return self

    def testSorted(self):
        for i, spec in enumerate(self.specs):
            idx = np.where(np.diff(np.argsort(spec.peaks[:,0]))!=1)
            if idx[0].size:
                return False
        return True
            
