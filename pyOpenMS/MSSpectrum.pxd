from string cimport *
from InstrumentSettings cimport *

cdef extern from "<OpenMS/KERNEL/MSSpectrum.h>" namespace "OpenMS":

    cdef cppclass PeakT:
        pass

    cdef cppclass MSSpectrum[PeakT]:
        MSSpectrum()
        double getRT()
        void   setRT(double)
        unsigned int getMSLevel()
        void setMSLevel(unsigned int)

        string getName()
        void setName(string)

        int size()
        PeakT operator[](int)

        InstrumentSettings getInstrumentSettings()

        

