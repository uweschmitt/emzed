
cdef class _MSExperiment1D:

    cdef MSExperiment[Peak1D, ChromatogramPeak] * inst
    
    def __cinit__(self):
        self.inst = new MSExperiment[Peak1D, ChromatogramPeak] ()
