import numpy as np
import scipy.optimize as opt

from pylab import *

data =np.loadtxt("eic.csv", delimiter=";")



x = data[:,0]
y = data[:,1]

imax = argmax(y)+3
print imax
x = x[:imax]
y = y[:imax]

#imax = sum(y<7)
#print imax
#print y[imax]
#
#x=x[:imax]
#y=y[:imax]


def fun(param, xvec):
    A, mu, s1 = param
    p=2
    return A * np.exp(-(x-mu)**p / s1) 

def err(param, xvec, yvec):
    return fun(param, xvec)-yvec

A     = max(y)
mu    = (x[-1]+x[0])/2.0 # mid

s1    = s2 = 1.0

p     = 2.0

A = 1.6e5
s1 = 1.7e0
s2 = 4.2e-1
mu= 2.19e1


A = max(y)
mu = x[-1]
s1 = 1.0
p = 2.0

param = A, mu, s1
print param

param, success = opt.leastsq(err, param, args = (x, y))
#print opt.leastsq(err, param, args = (x, y), full_output=True)

print success
#print info
print param

plot(x,y)
print x[:20]
print
print param
print
print len(fun(param,x[:20]))
plot(x, fun(param, x))

show()
exit()

from scipy.interpolate import splrep, splev

figure()

tck = splrep(x,y, s=100000)
print len(tck[0]), len(x)

f = splev(x, tck)
#f2= interp1d(x,y,kind="cubic", s=100)

plot(x,y)
plot(x,f)
show()



