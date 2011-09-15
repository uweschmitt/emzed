from PeakIntegrator import PeakIntegrator
import numpy as np
import scipy.optimize as opt

class AsymmetricGaussIntegrator(PeakIntegrator):

    def __init__(self, **kw):
        super(AsymmetricGaussIntegrator, self).__init__(kw)

    def getInfo(self):
        return "AsymmetricGaussIntegrator" 


    def smoothed(self, allrts, rts, chromatogram):

        def fun_eval(param, rts):
            A, s1, s2, mu = param
            isleft = rts < mu
            svec = s1 + isleft * (s2-s1)
            return A * np.exp(-(rts-mu)**2 / svec **2) 

        def err(param, rts, values):
            return fun_eval(param, rts) - values

        
        imax = np.argmax(chromatogram)
        A = chromatogram[imax]
        mu = rts[imax]
        s1 = s2 = 1.0

        param = A, s1, s2, mu

        param, success = opt.leastsq(err, param, args=(rts, chromatogram))

        return allrts, fun_eval(param, allrts)


        


        


        

        
        
        
