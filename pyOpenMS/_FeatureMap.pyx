cdef class _FeatureMap:

    cdef FeatureMap[Feature] * inst

    def __cinit__(self, init=True):
        if init:
            inst = new FeatureMap[Feature]()

    
