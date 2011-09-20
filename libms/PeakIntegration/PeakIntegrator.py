import numpy as np
from   libms.pyOpenMS import intensityInRange

class PeakIntegrator(object):

    def __init__(self, config=None):
        self.config = config
        self.peakMap = None

    def setPeakMap(self, peakMap):
        self.peakMap = peakMap
        self.allrts  = sorted([ spec.RT for spec in self.peakMap.specs ])
        self.allpeaks = [ spec.peaks for spec in self.peakMap.specs]

    def integrate(self, mzmin, mzmax, rtmin, rtmax):

        assert self.peakMap is not None

        ms1specs = [spec for spec in self.peakMap.specs if spec.msLevel == 1]

        peaksl = [ spec.peaks for spec in ms1specs if rtmin <= spec.RT <=rtmax ]
        chromatogram = np.array([ intensityInRange(peaks, mzmin, mzmax) for peaks in peaksl ])

        rts  = [ spec.RT for spec in ms1specs if rtmin <= spec.RT <=rtmax ]
        
        if len(rts)==0:
            return dict(area=0, rmse=0)

        fullchromatogram = [ intensityInRange(peaks, mzmin, mzmax) for peaks in self.allpeaks ]
        area, rmse, usedrts, smoothed = self.integrator(self.allrts, fullchromatogram, rts, chromatogram)

        return dict(area=area, rmse=rmse, intrts=usedrts,smoothed=smoothed)

    def smoothed(self, *a):
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

            
        

        
        



