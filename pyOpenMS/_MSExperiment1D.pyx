
cdef class _MSExperiment1D:

    cdef MSExperiment[Peak1D, ChromatogramPeak] * inst
    
    def __cinit__(self, init=True):
        if init:
           self.inst = new MSExperiment[Peak1D, ChromatogramPeak] ()

    #def get2DData(self):
        #self._get2DData()    

    #cdef _get2DData(self):
         #cdef ContainerPeak1D * pl = new ContainerPeak1D()
         #self.inst.get2DData(deref(pl))
