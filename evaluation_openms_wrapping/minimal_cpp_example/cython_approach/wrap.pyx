from cython.operator cimport dereference as deref, address

from libcpp.list cimport list

cdef extern from "string" namespace "std": 
    cdef cppclass string: 
        string()
        string(char *)
        char* c_str() 


cdef extern from "example.h":
    cdef cppclass Item:
         Item()
         Item( Item& )
         Item(string)
         void setD(string)
         string getD()

    cdef cppclass Container:
         Item getFront()
         Item getBack()
         void addItem(Item it)
         int  size()
         list[Item] getItems()


cdef extern from "example.h" namespace "Filler":
         void filler(int, Container)
         void throwException() except+


def test_excption():
        throwException()


cdef class StringWrapper:
    
    cdef string *s

    def __cinit__(self, char *ss):
         self.s = new string(ss)

    def __dealloc__(self):
         del self.s
    
    cdef c_str(self):
        return self.s.c_str()

    cdef string getS(self):
        return deref(self.s)
    

cdef class PyItem:

    cdef Item *it  

    def __cinit__(self) : 
        self.it = new Item()

    def __dealloc__(self):
        del self.it

    def getD(self):
        return self.it.getD().c_str()

    def setD(self, char * d):
        cdef string * s = new string(d)
        self.it.setD( deref(s))
        del s


cdef PyItemFromItem(Item *i):
     rv = PyItem()
     del rv.it
     rv.it = i
     return rv

cdef class PyContainer:

    cdef Container *c

    def __cinit__(self):
        self.c = new Container()

    def __dealloc__(self):
        del self.c

    def __len__(self):
        return self.c.size()

    def getFront(self):
        return PyItemFromItem(new Item(self.c.getFront()))

    def getBack(self):
        return PyItemFromItem(new Item(self.c.getBack()))
        
    def getItems(self):
        cdef list[Item] items = self.c.getItems()
        cdef Item it
        rv = []
        while not items.empty():
            it = items.front() # nur ref
            rv.append(PyItemFromItem(new Item(it))) # kopie von Item !
            items.pop_front()
        return rv
             

cpdef fill(int n, PyContainer c):
    filler(n, deref(c.c))

def runalot():
    for i in range(1000):
        cc = PyContainer()
        fill(1000, cc)




