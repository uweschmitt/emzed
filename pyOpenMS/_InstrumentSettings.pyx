from Polarity cimport *

cdef class _InstrumentSettings:

    cdef InstrumentSettings * inst

    def __cinit__(self, init = True):
        if init:
            self.inst = new InstrumentSettings()

    def __dealloc__(self):
        del self.inst

    def getPolarity(self):
        return _Polarity(self.inst.getPolarity())
