from cython.operator cimport dereference as deref, address

from MSSpectrum cimport *

cdef extern from "<OpenMS/KERNEL/MSExperiment.h>" namespace "OpenMS":

    cdef cppclass MSExperiment[PeakT, ChromoPeakT]:
        MSExperiment()
        double getMinMZ()
        double getMaxMZ()
        double getMinRT()
        double getMaxRT()
        void sortSpectra(bool)
        int   size()
        MSSpectrum[PeakT] operator[](int)
    

