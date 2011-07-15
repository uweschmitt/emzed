from libcpp.list   cimport list
from libcpp.vector cimport vector

from cython.operator cimport dereference as deref, address

from Feature cimport *
from FeatureMap cimport *

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

    def _push_back(self, _Feature f):
        cdef Feature * fi = f.inst
        self.inst.push_back(deref(fi))

    def __len__(self):
        return self.inst.size()
