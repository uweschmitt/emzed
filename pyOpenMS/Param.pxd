
from string cimport *
from InstrumentSettings cimport *
from DataValue cimport *

cdef extern from "<OpenMS/DATASTRUCTURES/Param.h>" namespace "OpenMS":


    cdef cppclass Param:
        Param()
        Param(Param)
        void setValue(string, DataValue)
        DataValue getValue(string)
        void store(string)
        void load(string)

        


