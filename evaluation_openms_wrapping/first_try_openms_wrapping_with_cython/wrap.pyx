from cython.operator cimport dereference as deref, address

from libcpp.list   cimport list
from libcpp.vector cimport vector

cdef extern from "string" namespace "std": 
    cdef cppclass string: 
        string()
        string(char *)
        char* c_str() 

cdef extern from "<OpenMS/KERNEL/Feature.h>" namespace "OpenMS":

    cdef cppclass Feature:
        Feature()

cdef extern from "<OpenMS/KERNEL/FeatureMap.h>" namespace "OpenMS":

    cdef cppclass FeatureMap[T]:
        FeatureMap()
        void push_back(Feature)
        int  size()





#cdef Feature * f = new Feature()
#cdef FeatureMap[Feature] *fm = new FeatureMap[Feature]()
#print fm.size()
#fm.push_back(deref(f))
#print fm.size()


cdef class _Feature:

    cdef Feature *inst

    def __cinit__(self):
        self.inst = new Feature()

    def __dealloc__(self):
        del self.inst

cdef class _FeatureMap:

    cdef FeatureMap[Feature] *inst 

    def __cinit__(self):
        self.inst = new FeatureMap[Feature]()

    def __dealloc__(self):
        del self.inst

    def push_back(self, f):
        self._push_back(f)

    cdef _push_back(self, _Feature f):
        cdef Feature * fi = f.inst
        self.inst.push_back(deref(fi))

    def __len__(self):
        return self.inst.size()
        




