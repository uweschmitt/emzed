from cython.operator cimport dereference as deref, address
from libcpp.vector cimport *

from string cimport *

from Feature cimport *
from FeatureMap cimport *
from MSExperiment cimport *
from MSSpectrum   cimport *
from MzXMLFile    cimport *

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




cdef class _MSSpectrum1D:

    cdef MSSpectrum[Peak1D] * inst

    def __cinit__(self):
        self.inst = new MSSpectrum[Peak1D] ()

    def getRT(self):
        return self.inst.getRT()

    def setRT(self, double value):
        self.inst.setRT(value)

    def getMSLevel(self):
        return self.inst.getRT()

    def setMSLevel(self, unsigned int value):
        self.inst.setMSLevel(value)

    def setName(self, char *name):
        cdef string* sname = new string(name)
        self.inst.setName(deref(sname))
        del sname
        
    def getName(self):
        return self.inst.getName().c_str()

    def __str__(self):
        #toString(deref(self.inst))
        return "<dummy>"
        #pass


cdef class _MSExperiment1D:

    cdef MSExperiment[Peak1D, ChromatogramPeak] * inst
    
    def __cinit__(self, init=True):
        if init:
           self.inst = new MSExperiment[Peak1D, ChromatogramPeak] ()

    #def get2DData(self):
        #self._get2DData()    

    #cdef _get2DData(self):
         #cdef ContainerPeak1D * pl = new ContainerPeak1D()
         #self.inst.get2DData(deref(pl))


cdef class _MzXMLFile:

    cdef MzXMLFile * inst 

    def __cinit__(self):
        self.inst = new MzXMLFile()

    def load(self, char * path):
        cdef string * s = new string(path)
        cdef MSExperiment[Peak1D, ChromatogramPeak] * exp = new MSExperiment[Peak1D, ChromatogramPeak]()
        self.inst.load(deref(s), deref(exp))
        rv = _MSExperiment1D(False)
        rv.inst = exp
        del s
        return rv


    
        
