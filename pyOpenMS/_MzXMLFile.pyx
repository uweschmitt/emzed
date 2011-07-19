
cpdef loadMzXMLFile( char * path):
    cdef MSExperiment[Peak1D, ChromatogramPeak] * exp = new MSExperiment[Peak1D, ChromatogramPeak]()
    cdef string * s = new string(path)
    cdef MzXMLFile * inst = new MzXMLFile()
    inst.load(deref(s), deref(exp))
    del s
    rv = _PeakMap(False)
    rv.inst = exp
    del inst
    return rv

