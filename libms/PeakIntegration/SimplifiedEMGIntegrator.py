from PeakIntegrator import PeakIntegrator
import numpy as np
import scipy.optimize as opt
import scipy.special  as special
import math
import sys
import StringIO

class SimplifiedEMGIntegrator(PeakIntegrator):

    def __init__(self, **kw):
        super(SimplifiedEMGIntegrator, self).__init__(kw)
        self.xtol = kw.get("xtol")

    def __str__(self):
        info = "default" if self.xtol is None else "%.2e" % self.xtol
        return "SimplifiedEMGIntegrator, xtol=%s" %  info

    @staticmethod
    def __fun_eval(param, rts):
        #print param
        h, z, w, s = param 
        nominator = np.exp(w*w/2.0/s/s - (rts-z)/ s)
        denominator = 1 + np.exp(-2.4055/math.sqrt(2.0) * ((rts-z)/w - w/s))
        return h*w/s * math.sqrt(2*math.pi) * nominator / denominator

    @staticmethod
    def __err(param, rts, values):
        return SimplifiedEMGIntegrator.__fun_eval(param, rts) - values

    def integrator(self, allrts, fullchromatogram, rts, chromatogram):

        """ 
             model is simplified EMG
        """

        if len(rts)<4:
            rmse = 1.0/math.sqrt(len(rts))*np.linalg.norm(chromatogram)
            return 0.0, rmse, (0.0, rts[0], 1.0, 0.0)
            
        imax = np.argmax(chromatogram)
        h = chromatogram[imax]
        z = rts[imax]
        w = s = 5.0
        rts = np.array(rts)
        
        param = h, z, w, s
        sys.stdout = sys.stderr = StringIO.StringIO()
        try:
            if self.xtol is None:
                param, ok = opt.leastsq(SimplifiedEMGIntegrator.__err, param, 
                                        args=(rts, chromatogram))
            else:
                param, ok = opt.leastsq(SimplifiedEMGIntegrator.__err, param, 
                                        args=(rts, chromatogram), xtol=self.xtol)
        finally:
            sys.stdout, sys.stderr = sys.__stdout__, sys.__stderr__

        h, z, w, s = param

        if ok not in [1,2,3,4] or s<=0 or w<=0: # failed
            area = 0
            rmse = 1.0/math.sqrt(len(rts))*np.linalg.norm(chromatogram)
        else:
            smoothed = SimplifiedEMGIntegrator.__fun_eval(param, allrts)
            smoothed[np.isnan(smoothed)]=0.0
            area = self.trapez(allrts, smoothed)
            rmse = 1/math.sqrt(len(allrts)) * np.linalg.norm(smoothed - fullchromatogram)
        #if np.isnan(area):
        #   area = 0.0
        #   rmse = 1.0/math.sqrt(len(rts))*np.linalg.norm(chromatogram)

        return area, rmse, param

    def getSmoothed(self, rtvalues, params):
        return rtvalues, SimplifiedEMGIntegrator.__fun_eval(params, np.array(rtvalues))


        
