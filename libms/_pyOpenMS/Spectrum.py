import numpy as np

class Spectrum(object):

    def __init__(self, RT, peaks, data=None):
        self.RT = RT
        self.peaks = np.array(peaks, dtype=np.float32)
        if data:
                self.polarization, self.msLevel, self.precursors, self.id = data
        else:
                self.polarization, self.msLevel, self.precursors, self.id = None, 1, [], None

    def __str__(self):
        return str((self.RT, self.peaks, self.polarization, 
                    self.msLevel, self.precursors, self.id ))

    def __len__(self):
        return self.peaks.shape[0]

    def removeZeroIntensities(self):
        MZ, I = 0, 1
        self.peaks = self.peaks[self.peaks[:,I]>0]
        return self

    def sortByMz(self):
        MZ, I  = 0, 1
        perm = np.argsort(self.peaks[:,MZ])
        self.peaks = self.peaks[perm,:]
        assert self.peaks.base is None
        return self

    

     
        
