
class Spectrum(object):

    def __init__(self, RT, peaks, data=None):
        self.RT = RT
        self.peaks = peaks
        if data:
                self.polarization, self.msLevel, self.precursors = data
        else:
                self.polarization, self.msLevel, self.precursors = None, 1, []

    def __str__(self):
        return str((self.RT, self.peaks, self.polarization, self.msLevel, self.precursors ))
        
