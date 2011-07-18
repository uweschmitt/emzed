from Feature cimport *

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
