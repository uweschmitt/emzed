from PeakIntegrator import PeakIntegrator
import numpy as np
import scipy.optimize as opt

class AssymetricGaussIntegrator(PeakIntegrator):

    def __init__(self, **kw):
        super(AssymetricGaussIntegrator, self).__init__(kw)

    def getInfo(self):
        return "AssymetricGaussIntegrator" 


    def smoothed(self, chromatogram):

        def fun_eval(param, rts):
            A, s1, s2, mu = param
            isleft = rts < mu
            svec = s1 + isleft * (s2-s1)
            return A * np.exp(-(rts-mu)**2 / svec **2) 

        def err(param, rts, values):
            return fun_eval(param, rts) - values

        
        rts = chromatogram[:,0] 
        values = chromatogram[:,1]

        imax = np.argmax(values)
        A = values[imax]
        mu = rts[imax]
        s1 = s2 = 1.0

        param = A, s1, s2, mu

        param, success = opt.leastsq(err, param, args=(rts, values))

        return fun_eval(param, rts)


        


        


        

        
        
        
