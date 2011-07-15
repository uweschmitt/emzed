from MSExperiment cimport *

cdef extern from "<OpenMS/KERNEL/MSExperiment.h>" namespace "OpenMS":
    cdef cppclass Peak1D:
        pass

    cdef cppclass ChromatogramPeak:
        pass

    cdef cppclass MSExperiment[PeakT, ChromoPeakT]:
        MSExperiment()
        
