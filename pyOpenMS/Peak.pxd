
cdef extern from "<OpenMS/KERNEL/Peak1D.h>" namespace "OpenMS":
    
    cdef cppclass Peak1D:
        double getMZ() 
