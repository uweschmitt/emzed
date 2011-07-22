from pxd.FeatureFinder cimport FeatureFinder as FeatureFinder_
from pxd.MSExperiment cimport *
from pxd.FeatureMap cimport FeatureMap as FeatureMap_
from pxd.Feature cimport Feature as Feature_


cdef class FeatureFinder:

    cdef FeatureFinder_ * inst 
    cdef dict params
    cdef string * method

    def __cinit__(self, char * method):
        self.inst = new FeatureFinder_()
        self.method = new string(method)
        self.params = paramToDict(self.inst.getParameters(deref(self.method)))

    def __dealloc__(self):
        del self.method
        del self.inst

    def getParameters(self):    
        return self.params

    def updateParams(self, dd):
        self.params.update(dd)
        return self

    def run(self, pm):
        assert isinstance(pm, PeakMap)
        cdef MSExperiment[Peak1D, ChromatogramPeak] pm_ = OpenMsPeakMapFromPy(pm)
        pm_.updateRanges()
        cdef Param p = dictToParam(self.params)
        cdef FeatureMap_[Feature_] seeds
        cdef FeatureMap_[Feature_] out
        self.inst.run(deref(self.method), pm_, out, p, seeds)
        return OpenMsFeatureMapToPy(out)




    
        
