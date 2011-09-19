from PeakIntegrator import PeakIntegrator
import numpy as np
import scipy.optimize as opt
import scipy.special  as special
import math

class AsymmetricGaussIntegrator(PeakIntegrator):

    def __init__(self, **kw):
        super(AsymmetricGaussIntegrator, self).__init__(kw)
        self.gtol = kw.get("gtol")

    def __str__(self):
        return "AsymmetricGaussIntegrator, gtol=%r"  % self.gtol


    def integrator(self, allrts, fullchromatogram, rts, chromatogram):

        """ model is to fit  A * exp ( (x-mu)**2 / s(x) ), where

            s(x) = s1 if x < mu else s2

        """

        def fun_eval(param, rts):
            A, s1, s2, mu = param
            isleft = rts < mu
            svec = s2 + isleft * (s1-s2)
            rv = np.exp(-(rts-mu)**2 / svec ) 
            return A*rv

        def err(param, rts, values):
            return fun_eval(param, rts) - values


        def diff(param, rts, values):

            res = np.zeros((len(rts), len(param)))
            fun = fun_eval(param, rts)
            
            A, s1, s2, mu = param
            isleft = rts < mu

            #area = self.trapez(rts, fun)

            res[:,0] = fun / A
            res[:,1] = -isleft * fun / s1
            res[:,2] = -(1-isleft) * fun / s2
            res[:,3] = 2*(rts-mu) * fun
            return res


        if len(rts)<4:
            return 0, 1e30, allrts, np.zeros_like(allrts)
            
        imax = np.argmax(chromatogram)
        A = chromatogram[imax]
        mu = rts[imax]
        s1 = s2 = 0.1

        param = A, s1, s2, mu

        old_opt = np.seterr(all="ignore")
        param, success = opt.leastsq(err, param, Dfun = None, gtol = self.gtol, args=(rts, chromatogram))
        np.seterr(**old_opt)
        A, s1, s2, mu = param

        smoothed = fun_eval(param, allrts)
        area = self.trapez(allrts, smoothed)
        rmse = 1/math.sqrt(len(allrts)) * np.linalg.norm(smoothed - fullchromatogram)

        #import pylab
        #pylab.plot(allrts, fullchromatogram)
        #pylab.plot(allrts, smoothed)
        #pylab.plot(rts, fun_eval(param, rts))
        #pylab.show()
        
        return area, rmse, allrts, smoothed


        
