from PeakIntegrator import PeakIntegrator
import numpy as np
import scipy.optimize as opt
import math

class AsymmetricGaussIntegrator(PeakIntegrator):

    def __init__(self, **kw):
        super(AsymmetricGaussIntegrator, self).__init__(kw)
        self.gtol = kw.get("gtol")

    def __str__(self):
        info = "default" if self.gtol is None else "%.2e" % self.gtol
        return "AsymmetricGaussIntegrator, gtol=%s" %  info

    @staticmethod
    def __fun_eval(param, rts):
        A, s1, s2, mu = param
        isleft = rts < mu
        svec = s2 + isleft * (s1-s2)
        rv = np.exp(-(rts-mu)**2 / svec )
        return A*rv

    @staticmethod
    def __err(param, rts, values):
        return AsymmetricGaussIntegrator.__fun_eval(param, rts) - values

    def integrator(self, allrts, fullchromatogram, rts, chromatogram):

        """ model is to fit  A * exp ( (x-mu)**2 / s(x) ), where

            s(x) = s1 if x < mu else s2

        """

        if len(rts)<4:
            rmse = 1.0/math.sqrt(len(rts))*np.linalg.norm(chromatogram)
            return 0.0, rmse, (0.0, 1.0, 1.0, 0.0)

        imax = np.argmax(chromatogram)
        A = chromatogram[imax]
        mu = rts[imax]
        s1 = s2 = 0.5 # 1.0
        if self.gtol is None:
            (A, s1, s2, mu), ok = opt.leastsq(AsymmetricGaussIntegrator.__err,
                                              (A, s1, s2, mu),
                                              args=(rts, chromatogram))
        else:
            (A, s1, s2, mu), ok = opt.leastsq(AsymmetricGaussIntegrator.__err,
                                              (A, s1, s2, mu), gtol = self.gtol,
                                              args=(rts, chromatogram))

        if ok not in [1,2,3,4] or s1<0 or s2<0 : # failed
            area = np.nan
            rmse = np.nan
        else:
            smoothed = AsymmetricGaussIntegrator.__fun_eval( (A, s1, s2, mu), allrts)
            area = self.trapez(allrts, smoothed)
            rmse = 1/math.sqrt(len(allrts)) * np.linalg.norm(smoothed - fullchromatogram)

        return area, rmse, (A, s1, s2, mu)


    def getSmoothed(self, rtvalues, params):
        return rtvalues, AsymmetricGaussIntegrator.__fun_eval(params, np.array(rtvalues))


