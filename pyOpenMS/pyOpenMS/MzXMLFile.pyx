from pyOpenMS.pxd.MzXMLFile cimport *
from pyOpenMS.pxd.MSExperiment cimport *
from Spectrum import Spectrum


def loadMzXMLFile(char *path):
    cdef MSExperiment[Peak1D, ChromatogramPeak] mse 
    cdef MzXMLFile f
    cdef string * s = new string(path)
    f.load(deref(s), mse)
    del s
    return OpenMsPeakMapToPy(mse) 

def saveMzXMLFile(peakMap, char *path):
    assert isinstance(peakMap, PeakMap)
    cdef MSExperiment[Peak1D, ChromatogramPeak] peakMap_
    peakMap_ = OpenMsPeakMapFromPy(peakMap) 
    cdef MzXMLFile f
    cdef string * s = new string(path)
    f.store(deref(s), peakMap_)
    del s
    
