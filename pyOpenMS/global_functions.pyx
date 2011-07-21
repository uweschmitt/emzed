
# this file has a strange name, because when collecing all _*pyx files in setup.py
# the global functions have to appear at the end to avoid unknown types errors.


cdef _WaveletFeatureFinder(MSExperiment[Peak1D, ChromatogramPeak] * in_, FeatureMap[Feature] * out, Param p):
    cdef FeatureMap[Feature] seeds
    cdef FeatureFinder ff #  = new FeatureFinder()
    cdef string * typ = new string("typ")
    in_.updateRanges()
    ff.run(deref(typ), deref(in_), deref(out), p, seeds)
    del typ 

def WaveletFeatureFinder(_PeakMap in_, _Param p):
    cdef FeatureMap[Feature] * out = new FeatureMap[Feature]()
    _WaveletFeatureFinder(in_.inst, out, deref(p.inst))
    rv = _FeatureMap(False)
    rv.inst = out
    return rv
    

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

    
    
