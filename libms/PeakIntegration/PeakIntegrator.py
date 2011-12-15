import numpy as np

class PeakIntegrator(object):

    def __init__(self, config=None):
        self.config = config
        self.peakMap = None

    def setPeakMap(self, peakMap):
        self.peakMap = peakMap
        self.ms1specs = [spec for spec in self.peakMap.spectra if spec.msLevel == 1]
        self.allrts  = sorted([ spec.rt for spec in self.ms1specs])

    def integrate(self, mzmin, mzmax, rtmin, rtmax):

        assert self.peakMap is not None

        rts, chromatogram = self.peakMap.chromatogram(mzmin, mzmax, rtmin,\
                                                      rtmax)
        if len(rts)==0:
            return dict(area=0, rmse=0, params=None)

        allrts, fullchrom = self.peakMap.chromatogram(mzmin, mzmax)
        area, rmse, params = self.integrator(allrts, fullchrom, rts,
                                             chromatogram)

        return dict(area=area, rmse=rmse, params=params)

    def getSmoothed(self, *a):
        raise Exception("not implemented")

    def trapez(self, x, y):
        assert len(x)==len(y), "x, y have different length"

        x = np.array(x)
        y = np.array(y)

        dx = x[1:] - x[:-1]
        sy = 0.5*(y[1:] + y[:-1])
        return np.dot(dx, sy)


if __name__ == "__main__":

        pi = PeakIntegrator(None)
        x = [1,2,5,6,9]
        y = [1,2,1,4,-7]

        pi.trapez(x,y)
