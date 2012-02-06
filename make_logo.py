import pylab as pl
import numpy as np


x=np.arange(0, 10, 0.01)

def make_bump(center, w=0.45, x=x):
    return np.exp(-(x-center)*(x-center)/w)

y = make_bump(1.0)
y+= 0.6*make_bump(3.0)
y+= 0.45*make_bump(5.0)
y+= 0.3*make_bump(7.0)

pl.plot(x,y)
ax = pl.gca()
ax.yaxis.set_visible(False)
ax.xaxis.set_visible(False)

pl.show()




