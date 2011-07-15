from Feature cimport *

cdef extern from "<OpenMS/KERNEL/FeatureMap.h>" namespace "OpenMS":

    # declare ahead:
    cdef cppclass Feature:
        pass

    # needed members in class + their signatures:
    cdef cppclass FeatureMap[T]:
        FeatureMap()
        void push_back(Feature)
        int  size()
