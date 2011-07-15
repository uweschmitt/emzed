from string cimport *

cdef extern from "<OpenMS/KERNEL/MSSpectrum.h>" namespace "OpenMS":

    cdef cppclass MSSpectrum[PeakT]:
        MSSpectrum()
        double getRT()
        void   setRT(double)
        unsigned int getMSLevel()
        void setMSLevel(unsigned int)

        string getName()
        void setName(string)

        

