cdef class Function:
    cpdef double evaluate(self, double x) except *:
        return 0


cdef class Halbkreis(Function):

     cpdef double evaluate(self, double x) except *:
        return (1-x*x)**0.5

def integrate(Function f, double a, double b, int N):
  cdef int i
  cdef double s, dx
  if f is None:
      raise ValueError("f cannot be None")
  s = 0
  dx = (b-a)/N
  for i in range(N):
      s += f.evaluate(a+i*dx)
  return s * dx

print "PI approx ", (integrate(Halbkreis(), -1, 1, 20000))*2.0


