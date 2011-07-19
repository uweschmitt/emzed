

cdef class _Param:

    cdef Param * inst

    def __cinit__(self):
        self.inst = new Param()

    def __dealloc__(self):
        del self.inst

    def load(self, char* fname):
        cdef string *stemp = new string(fname)
        self.inst.load(deref(stemp))
        del stemp

    def store(self, char* fname):
        cdef string *stemp = new string(fname)
        self.inst.store(deref(stemp))
        del stemp

    cdef DataValue getValue(self, char * name):
    
        cdef DataValue data
        cdef string *stemp = new string(name)
        data = self.inst.getValue(deref(stemp))
        del stemp
        return data

    def getStrValue(self, char* key):
        return self.getValue(key).toChar()
   
    def getIntValue(self, char* key):
        return <long>self.getValue(key)

    def getFloatValue(self, char* key):
        return <double>self.getValue(key)
        
    cdef void setValue(self, char *key, DataValue * value):
        cdef string * stemp = new string(key)
        self.inst.setValue(deref(stemp), deref(value))
        del stemp

    def setStrValue(self, char *key, char * value):
        self.setValue(key, new DataValue(value))
        
    def setIntValue(self, char *key, long value):
        self.setValue(key, new DataValue(value))
    
    def setFloatValue(self, char *key, double value):
        self.setValue(key, new DataValue(value))
        


