
cdef class _MSExperiment1D:

    cdef MSExperiment[Peak1D, ChromatogramPeak] * inst
    
    def __cinit__(self):
        self.inst = new MSExperiment[Peak1D, ChromatogramPeak] ()

    def get2DData(self):
        _get2DData(self)    

    cdef _get2DData(self):
         cdef list[Peak1] * pl = new list[Peak1]()
        
