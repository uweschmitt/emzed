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

def savitzky_golaycoeff(window_size, order, deriv=0):

    try:
        window_size = np.abs(np.int(window_size))
        order = np.abs(np.int(order))
    except ValueError, msg:
        raise ValueError("window_size and order have to be of type int")
    if window_size % 2 != 1 or window_size < 1:
        raise TypeError("window_size size must be a positive odd number")
    if window_size < order + 2:
        raise TypeError("window_size is too small for the polynomials order")
    order_range = range(order+1)
    half_window = (window_size -1) // 2
    # precompute coefficients
    b = np.mat([[k**i for i in order_range] for k in range(-half_window, half_window+1)])
    m = np.linalg.pinv(b).A[deriv]
    # pad the signal at the extremes with
    # values taken from the signal itself
    return m

def savitzky_golay_smooth(y, w):
    half_window = len(w)/2
    firstvals = y[0] - np.abs( y[1:half_window+1][::-1] - y[0] )
    lastvals = y[-1] + np.abs(y[-half_window-1:-1][::-1] - y[-1])
    y = np.concatenate((firstvals, y, lastvals))
    return np.convolve( w, y, mode='valid')

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

    plot(x,y)
    plot(x, fun(param, x))

def dosmooth(data):

    m = savitzky_golaycoeff(11, 2)

    x = data[:,0]
    y = data[:,1]

    plot(x,y)
    plot(x, savitzky_golay_smooth(y, m))

    


import time, glob

datasets = []
for p in glob.glob("eic*.csv"):
    datasets.append(np.loadtxt(p, delimiter=";"))

print "got datasets"

started = time.time()
for i, ds in enumerate(datasets):
    figure()
    subplot(2,1,1)
    dofit(ds)
    subplot(2,1,2)
    dosmooth(ds)
    savefig("peakmodel%03d.png" % i)

print time.time()-started


