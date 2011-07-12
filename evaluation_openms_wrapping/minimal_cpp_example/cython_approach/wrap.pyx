from cython.operator import dereference
from libcpp.list cimport list

cdef extern from "string" namespace "std": 
    cdef cppclass string: 
        string()
        string(char *)
        char* c_str() 


cdef extern from "example.h":
    cdef cppclass Item:
         Item( Item& )
         Item(string)
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


cdef class PyItem:

    cdef Item *it  
    cdef string *name

    def __cinit__(self, char * name):
        self.name = new string(name)
        self.it = new Item(dereference(self.name))

    def __dealloc__(self):
        if self.name: 
           del self.name 
        del self.it

    def getD(self):
        return self.it.getD().c_str()


cdef class PyContainer:

    cdef Container *c

    def __cinit__(self):
        self.c = new Container()

    def __dealloc__(self):
        del self.c

    def __len__(self):
        return self.c.size()

    def getFront(self):
        cdef Item * tempitem = new Item(self.c.getFront())
        rv = PyItem(tempitem.getD().c_str())
        del tempitem
        return rv

    def getItems(self):
        cdef list[Item] items = self.c.getItems()


def fill(int n, PyContainer c):
    filler(n, dereference(c.c))

def runalot():
    for i in range(100):
        cc = PyContainer()
        fill(10000, cc)




