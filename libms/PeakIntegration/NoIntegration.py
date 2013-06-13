import PeakIntegrator

class NoIntegration(PeakIntegrator.PeakIntegrator):

    def __init__(self, *a, **kw):
        pass

    def setPeakMap(self, peakMap):
        pass

    def integrate(self, *a, **kw):
        return dict(area=None, rmse=None, params=None)

    def _getSmoothed(self, *a, **kw):
        return [], []
