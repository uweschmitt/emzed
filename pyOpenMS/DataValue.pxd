from string cimport *
from InstrumentSettings cimport *

cdef extern from "<OpenMS/DATASTRUCTURES/DataValue.h>" namespace "OpenMS":


    cdef cppclass DataValue:
        DataValue()
        DataValue(DataValue)
        DataValue(char *)
        DataValue(double)
        DataValue(long)
        char * toChar()

