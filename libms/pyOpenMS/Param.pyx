from libcpp.vector cimport *
from pxd.DataValue cimport *
from pxd.Param cimport *


cdef class _ParamInstance:

    cdef Param * p

    def __cinit__(self):
        self.p = new Param()
    
    def __dealloc__(self):
        del self.p



cdef paramToDict(Param p):
    cdef list[string] keys = getKeys(p)
    cdef list[string].iterator it = keys.begin()
    cdef dict rv = dict()
    cdef string skey
    cdef DataValue val
    while it != keys.end():
        skey = deref(it)
        try:
            val = p.getValue(skey)
        except:
            rv[skey.c_str()] =  None
        else:
            if val.valueType() == STRING_VALUE:
                rv[skey.c_str()] =  val.toChar()
            elif val.valueType() == INT_VALUE:
                rv[skey.c_str()] = <int> val
            elif val.valueType() == DOUBLE_VALUE:
                rv[skey.c_str()] = <double> val
            else:
                raise "not implemented !"
        it = next(it)
        
    return rv
        
    
   

cdef Param dictToParam(dict dd):
    cdef Param p
    cdef DataValue * dv
    cdef string * temps
    for key, value in dd.items():
        if isinstance(value, int) or isinstance(value, long):
            dv = new DataValue(<long>(value))
        if isinstance(value, float) :
            dv = new DataValue(<double>(value))
        if isinstance(value, str) :
            dv = new DataValue(<char *>value)
        temps = new string(key)
        p.setValue(deref(temps), deref(dv))
        del temps
    return p



def saveParam(dict dd, char * fname):
    cdef Param pp = dictToParam(dd)
    cdef string * stemp = new string(fname)
    pp.store(deref(stemp))
    del stemp

def loadParam(char * fname):
    cdef Param pp 
    cdef string * stemp = new string(fname)
    pp.load(deref(stemp))
    del stemp
    return paramToDict(pp) 

