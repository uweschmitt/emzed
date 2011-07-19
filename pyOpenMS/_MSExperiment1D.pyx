
cdef class _MSExperiment1D:

    cdef MSExperiment[Peak1D, ChromatogramPeak] * inst
    
    def __cinit__(self, init=True):
        if init:
           self.inst = new MSExperiment[Peak1D, ChromatogramPeak] ()

    def __dealloc__(self):
        del self.inst

    def getMinMZ(self):
        return self.inst.getMinMZ()

    def getMaxMZ(self):
        return self.inst.getMaxMZ()

    def getMinRT(self):
        return self.inst.getMinRT()

    def getMaxRT(self):
        return self.inst.getMaxRT()

    def sortSpectraByRT(self):
        self.inst.sortSpectra(False)
        return self

    def sortSpectraByRTAndMZ(self):
        self.inst.sortSpectra(True)
        return self

    def __len__(self):
        return self.inst.size()

    def __getitem__(self, int index):
        # create new instance via copy constructor
        cdef MSSpectrum[Peak1D] * spec = new MSSpectrum[Peak1D](deref(self.inst)[index])
        rv = _MSSpectrum1D(False)
        rv.inst = spec
        return rv

    #def get2DData(self):
        #self._get2DData()    

    #cdef _get2DData(self):
         #cdef ContainerPeak1D * pl = new ContainerPeak1D()
         #self.inst.get2DData(deref(pl))
