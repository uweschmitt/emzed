from cython.operator cimport dereference as deref, address
from MSExperiment cimport *
from libcpp.vector import *

cdef extern from "<OpenMS/KERNEL/MSExperiment.h>" namespace "OpenMS":
    cdef cppclass Peak1D:
        pass

    cdef cppclass ChromatogramPeak:
        pass

    cdef cppclass MSExperiment[PeakT, ChromoPeakT]:
        MSExperiment()
        #void get2DData(ContainerPeak1D)
        
