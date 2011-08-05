import numpy as np

class Spectrum(object):

    def __init__(self, RT, peaks, data=None):
        self.RT = RT
        self.peaks = np.array(peaks, dtype=np.float32)
        if data:
                self.polarization, self.msLevel, self.precursors = data
        else:
                self.polarization, self.msLevel, self.precursors = None, 1, []

    def __str__(self):
        return str((self.RT, self.peaks, self.polarization, 
                    self.msLevel, self.precursors ))

    def __len__(self):
        return self.peaks.shape[0]

    def removeZeroIntensities(self):
        MZ, I = 0, 1
        self.peaks = self.peaks[self.peaks[:,I]>0]

     
        
