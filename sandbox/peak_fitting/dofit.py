import numpy as np
import scipy.optimize as opt

from pylab import *


def fun(param, xvec):
    A, s1, s2, mu = param
    isleft = xvec < mu
    svec = s1 + isleft * (s2-s1)
    return A * np.exp(-(xvec-mu)**2 / svec **2) 

def err(param, xvec, yvec):
    return fun(param, xvec)-yvec


def dofit(data):

    x = data[:,0]
    y = data[:,1]

    A     = max(y)
    mu    = (x[-1]+x[0])/2.0 # mid

    s1    = s2 = 1.0

    param = A, s1, s2, mu

    param, success = opt.leastsq(err, param, args = (x, y))
    print success, param
    #print opt.leastsq(err, param, args = (x, y), full_output=True)

    figure()

    plot(x,y)
    plot(x, fun(param, x))


import time, glob

datasets = []
for p in glob.glob("eic*.csv"):
    datasets.append(np.loadtxt(p, delimiter=";"))

print "got datasets"

started = time.time()
for ds in datasets:
    dofit(ds)

print time.time()-started

show()
    

