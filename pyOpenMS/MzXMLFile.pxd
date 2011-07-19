
from MSExperiment  cimport *
from Peak cimport *
from string cimport *

cdef extern from "<OpenMS/FORMAT/MzXMLFile.h>" namespace "OpenMS":

    cdef cppclass MzXMLFile:
        MzXMLFile()
        void load(string, MSExperiment[Peak1D, ChromatogramPeak]) except+
