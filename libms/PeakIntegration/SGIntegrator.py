from PeakIntegrator import PeakIntegrator
import numpy as np

class SGIntegrator(PeakIntegrator):

    def __init__(self, **kw):

        super(SGIntegrator, self).__init__(kw)

        order = kw.get("order")
        window_size = kw.get("window_size")

        if order is None or window_size is None:
            raise Exception("need arguments order and window_size")

        self.weights = self._savitzky_golay_coeff(window_size, order)

    def getInfo(self):
        
        return "SGFiltering (window_size=%(window_size)d, order=%(order)d) followed by integration" % self.config

    def _savitzky_golay_coeff(self, window_size, order, deriv=0):
        """ from http://www.scipy.org/Cookbook/SavitzkyGolay """

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

    def _savitzky_golay_smooth(self, y, w):
        """ from http://www.scipy.org/Cookbook/SavitzkyGolay """

        half_window = len(w)/2
        firstvals = y[0] - np.abs( y[1:half_window+1][::-1] - y[0] )
        lastvals = y[-1] + np.abs(y[-half_window-1:-1][::-1] - y[-1])
        y = np.concatenate((firstvals, y, lastvals))
        return np.convolve( w, y, mode='valid')

    def smoothed(self, chromatogram):
        return self._savitzky_golay_smooth(chromatogram[:,1], self.weights)
        


        

        
        
        
