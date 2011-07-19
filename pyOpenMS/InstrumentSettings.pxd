from Polarity cimport *

cdef extern from "<OpenMS/METADATA/InstrumentSettings.h>" namespace "OpenMS":

    cdef cppclass InstrumentSettings:
        
        InstrumentSettings()
        InstrumentSettings(InstrumentSettings)
        Polarity getPolarity()
