import numpy as np
import scipy.interpolate
from   libms.pyOpenMS import intensityInRange

class PeakIntegrator(object):

    def __init__(self, config):
        self.config = config
        self.peakMap = None

    def setPeakMap(self, peakMap):
        self.peakMap = peakMap
        self.allrts  = sorted([ spec.RT for spec in self.peakMap.specs ])
        self.allpeaks = [ spec.peaks for spec in self.peakMap.specs]

    def integrate(self, mzmin, mzmax, rtmin, rtmax):

        assert self.peakMap is not None

        peaksl = [ spec.peaks for spec in self.peakMap.specs if rtmin <= spec.RT <=rtmax and spec.msLevel == 1]
        chromatogram = np.array([ intensityInRange(peaks, mzmin, mzmax) for peaks in peaksl ])

        rts  = [ spec.RT for spec in self.peakMap.specs if rtmin <= spec.RT <=rtmax ]
        
        if len(rts)==0:
            return dict(area=0, rmse=0)

        usedrts, smoothed = self.smoothed(self.allrts, rts, chromatogram)

        assert len(usedrts)==len(smoothed)

        area = self.trapez(usedrts, smoothed)

        # maybe the smoothed() call introduces rts not in self.allrts
        # so we interpolate the input to the usedrts in order to
        # get an estimation about the quality of the smoothing
        fullchromatogram = [ intensityInRange(peaks, mzmin, mzmax) for peaks in self.allpeaks ]
        cinterpolator = scipy.interpolate.interp1d(self.allrts, fullchromatogram)
        newc = cinterpolator(usedrts)
        rmse = np.sqrt( np.sum( (newc-smoothed)**2) / len(smoothed))
        #rmse = 0

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

            
        

        
        



