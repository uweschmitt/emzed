
cdef class _MzXMLFile:

    cdef MzXMLFile * inst 

    def __cinit__(self):
        self.inst = new MzXMLFile()

    def load(self, char * path):
        cdef string * s = new string(path)
        cdef MSExperiment[Peak1D, ChromatogramPeak] * exp = new MSExperiment[Peak1D, ChromatogramPeak]()
        self.inst.load(deref(s), deref(exp))
        rv = _MSExperiment1D(False)
        rv.inst = exp
        del s
        return rv

