from PeakIntegrator import PeakIntegrator
import numpy as np
import scipy.optimize as opt
import scipy.special  as special
import math

class SimplifiedEMGIntegrator(PeakIntegrator):

    def __str__(self):
        return "SimplifiedEMGIntegrator"

    @staticmethod
    def __fun_eval(param, rts):
        h, z, w, s = param
        nominator = np.exp(w*w/2.0/s/s - (x-z)/ s)
        denominator = 1 + np.exp(-2.4055/math.sqrt(2.0) * ((x-z)/w - w/s))
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
        w = s = 1.0
        
        param = h, z, w, s
        param, ok = opt.leastsq(SimplifiedEMGIntegrator.__err, param, 
                                args=(rts, chromatogram))
        h, z, w, s = param

        if ok not in [1,2,3,4] or s<0 or w<0: # failed
            area = np.nan
            rmse = np.nan
        else:
            smoothed = SimplifiedEMGIntegrator.__fun_eval(param, allrts)
            area = self.trapez(allrts, smoothed)
            rmse = 1/math.sqrt(len(allrts)) * np.linalg.norm(smoothed - fullchromatogram)

        return area, rmse, param

    def getSmoothed(self, rtvalues, params):
        return rtvalues, SimplifiedEMGIntegrator.__fun_eval(params, np.array(rtvalues))


        