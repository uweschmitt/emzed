

cdef class _Precursor:

    cdef Precursor * inst
    
    def __cinit__(self, init=True):
        if init:
           self.inst = new Precursor()

    def __dealloc__(self):
        del self.inst

    def getMZ(self):
        return self.inst.getMZ()

    def getIntensity(self):
        return self.inst.getIntensity()

    def __str__(self):
        return str( (self.getMZ(), self.getIntensity()))
