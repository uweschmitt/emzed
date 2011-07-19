from cython.operator cimport dereference as deref, address
#from MSExperiment cimport *
from MSSpectrum cimport *
from libcpp.vector cimport *

cdef extern from "<OpenMS/KERNEL/MSExperiment.h>" namespace "OpenMS":

    cdef cppclass ChromatogramPeak:
        pass

    cdef cppclass MSSpectrum[PeakT]:
        pass

    cdef cppclass MSExperiment[PeakT, ChromoPeakT]:
        MSExperiment()
        #void get2DData(ContainerPeak1D)
        double getMinMZ()
        double getMaxMZ()
        double getMinRT()
        double getMaxRT()
        void sortSpectra(bool)
        int   size()
        MSSpectrum[PeakT] operator[](int)
    
        
