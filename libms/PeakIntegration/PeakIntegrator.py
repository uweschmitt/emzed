import numpy as np

class PeakIntegrator(object):

    def __init__(self, config):
        self.config = config
        self.peakMap = None

    def setPeakMap(self, peakMap):
        self.peakMap = peakMap

    def integrate(self, mzmin, mzmax, rtmin, rtmax):

        assert self.peakMap is not None

        peaksl = [ spec.peaks for spec in self.peakMap.specs if rtmin <= spec.RT <=rtmax ]
        intensities = [ np.sum( (peaks[ (peaks[:,0] >= mzmin) * (peaks[:,0]<=mzmax)])[:,1]) for peaks in peaksl ]
        rts  = [ spec.RT for spec in self.peakMap.specs if rtmin <= spec.RT <=rtmax ]
        chromatogram = np.array(zip(rts, intensities))
        
        if len(rts)==0:
            return dict(area=0, rmse=0)

        smoothed = self.smoothed(chromatogram)

        area = sum(smoothed)
        rmse = np.sqrt( np.sum( (chromatogram[:,1]-smoothed)**2) / len(smoothed))

        return dict(area=area, rmse=rmse, rts=rts,smoothed=smoothed)

    def smoothed(self, chromatogram):
        raise Exception("not implemented")

        
        



