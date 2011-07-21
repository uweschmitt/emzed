
class Spectrum(object):

    def __init__(self, data=None):
        if data:
            self.RT, self.peaks, self.polarization, self.msLevel = data
        else:
            self.RT, self.peaks, self.polarization, self.msLevel=  None, [], None, None

    def __str__(self):
        return str((self.RT, self.peaks, self.polarization, self.msLevel ))
        
