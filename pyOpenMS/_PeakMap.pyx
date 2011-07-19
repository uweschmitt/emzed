
cdef class _PeakMap:

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
        if index<0:
            index = self.inst.size()+index
        # create new instance via copy constructor
        cdef MSSpectrum[Peak1D] * spec = new MSSpectrum[Peak1D](deref(self.inst)[index])
        rv = _PeakSpectrum(False)
        rv.inst = spec
        return rv


    def __iter__(self):
        return IterWrapper(self)


class IterWrapper:

    def __init__(self, container):
        self.container = container
        self.i = 0

    def __iter__(self): 
        return self

    def next(self):
        if self.i == len(self.container):
            raise StopIteration()
        rv = self.container[self.i]
        self.i+=1
        return rv
         
