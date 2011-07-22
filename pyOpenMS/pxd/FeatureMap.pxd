
cdef extern from "<OpenMS/KERNEL/FeatureMap.h>" namespace "OpenMS":

    cdef cppclass FeatureMap[T]:
        FeatureMap()
        T operator[](int)
        int size()
        void assign(vector[T].iterator, vector[T].iterator)
        void sortByIntensity(bool)
        void updateRanges()
        
        
