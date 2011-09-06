import numpy as np

class PeakMap(object):

    def __init__(self, specs = []):
        self.specs = specs
        self.meta  = dict()

    def __len__(self):
        return len(self.specs)


    def __iter__(self):
        return iter(self.specs)

    def filter(self, predicate):

        return PeakMap( [ s for s in self.specs if predicate(s) ] )

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
            
