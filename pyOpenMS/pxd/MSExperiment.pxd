from cython.operator cimport dereference as deref, address

from MSSpectrum cimport *
from Peak1D cimport *
from ChromatogramPeak cimport *

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
        void   updateRanges()
        vector[MSSpectrum[PeakT]].iterator begin()
        vector[MSSpectrum[PeakT]].iterator end()
        void  erase(vector[MSSpectrum[PeakT]].iterator)
        void push_back(MSSpectrum[PeakT])
       
    

