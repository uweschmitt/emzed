from pxd.MzXMLFile cimport *
from pxd.MSExperiment cimport *

def loadMzXMLFile(char *path):
    cdef MSExperiment[Peak1D, ChromatogramPeak] mse 
    cdef MzXMLFile f
    cdef string * s = new string(path)
    f.load(deref(s), mse)
    del s
    return OpenMsPeakMapToPy(mse) 
    
