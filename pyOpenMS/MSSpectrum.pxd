from string cimport *
from libcpp.vector cimport *
from InstrumentSettings cimport *
from Precursor cimport *

cdef extern from "<OpenMS/KERNEL/MSSpectrum.h>" namespace "OpenMS":

    cdef cppclass MSSpectrum[PeakT]:
        MSSpectrum()
        MSSpectrum(MSSpectrum)
        double getRT()
        void   setRT(double)
        unsigned int getMSLevel()
        void setMSLevel(unsigned int)

        string getName()
        void setName(string)

        int size()
        PeakT operator[](int)

        InstrumentSettings getInstrumentSettings()
        int findNearest(double) except+
        vector[Precursor] getPrecursors()

        

