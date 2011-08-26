from pyOpenMS.pxd.MzXMLFile cimport *
from pyOpenMS.pxd.MSExperiment cimport *
from Spectrum import Spectrum
cimport cpython


def loadMzXmlFile(char *path, cpython.bool sortByMz=True, cpython.bool removeZeroIntensities = True):
    cdef MSExperiment[Peak1D, ChromatogramPeak] mse = MSExperiment[Peak1D, ChromatogramPeak]()
    cdef MzXMLFile f = MzXMLFile()
    cdef string * s_path = new string(path)
    f.load(deref(s_path), mse)
    del s_path
    pm = OpenMsPeakMapToPy(mse) 
    if removeZeroIntensities:
        pm.removeZeroIntensities()
    if sortByMz:
        pm.sortByMz()
    pm.meta["source"] = cpython.PyString_FromString(path)
    return pm

def saveMzXmlFile(peakMap, char *path):
    assert isinstance(peakMap, PeakMap)
    cdef MSExperiment[Peak1D, ChromatogramPeak] peakMap_ # = MSExperiment[Peak1D, ChromatogramPeak]() 
    peakMap_ = OpenMsPeakMapFromPy(peakMap) 
    cdef MzXMLFile f = MzXMLFile()
    cdef string * s = new string(path)
    f.store(deref(s), peakMap_)
    del s
    
