from libc.stdlib cimport atoi
from libc.math cimport sin

#cdef extern from "math.h":
	#double sin(double)

def parse_int(char* s):
    assert s is not NULL, "byte string value is NULL"
    return atoi(s)   # note: atoi() has no error detection!

def f(double x):
    return (sin(x)-x)/sin(x)
