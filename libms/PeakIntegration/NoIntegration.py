
class NoIntegration(object):

    def __init__(self, *a, **kw):
        pass

    def setPeakMap(self, peakMap):
        pass

    def integrate(self, *a, **kw):
        return dict(area=None, rmse=None, params=None)

    def getSmoothed(self, *a, **kw):
        return [], []
