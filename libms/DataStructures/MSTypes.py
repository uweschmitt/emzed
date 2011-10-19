
"""

   pyOpenMS + some extensions

"""

import pyOpenMS 
import numpy as np
from copy import deepcopy, copy



class Spectrum(object):

    def __init__(self, peaks, rt, msLevel, polarity, precursors=[]):
        assert type(peaks) == np.ndarray, type(peaks)
        assert polarity in "0+-", "polarity must be +, - or 0"
        self.rt = rt
        self.peaks = peaks
        self.msLevel = msLevel
        self.precursors = precursors
        self.polarity = polarity

    @classmethod
    def fromMSSpectrum(clz, mspec):
        assert type(mspec) == pyOpenMS.MSSpectrum, type(mspec)
        pcs = [ (p.getMZ(), p.getIntensity()) for p in mspec.getPrecursors()]
        pol = { pyOpenMS.Polarity.POLNULL: '0',
                pyOpenMS.Polarity.POSITIVE: '+',
                pyOpenMS.Polarity.NEGATIVE: '-'
              }.get(mspec.getInstrumentSettings().getPolarity())
        res = clz(mspec.get_peaks(), mspec.getRT(), 
                  mspec.getMSLevel(), pol, pcs)
        return res

    def __len__(self):
        return self.peaks.shape[0]

    def __iter__(self):
        return iter(self.peaks)

    def intensityInRange(self, mzmin, mzmax):
        imin = self.peaks[:,0].searchsorted(mzmin)
        imax = self.peaks[:,0].searchsorted(mzmax, side='right')
        rv = np.sum(self.peaks[imin:imax,1])
        return rv


    def toMSSpectrum(self):
        spec = pyOpenMS.MSSpectrum()
        spec.setRT(self.rt)
        spec.setMSLevel(self.msLevel)
        ins = spec.getInstrumentSettings()
        pol = { '0' : pyOpenMS.Polarity.POLNULL,
                '+' : pyOpenMS.Polarity.POSITIVE,
                '-' : pyOpenMS.Polarity.NEGATIVE}[self.polarity]
        ins.setPolarity(pol)
        spec.setInstrumentSettings(ins)
        oms_pcs = []
        for mz, I in self.precursors:
            p=pyOpenMS.Precursor()
            p.setMZ(mz)
            p.setIntensity(I)
            oms_pcs.append(p)
        spec.setPrecursors(oms_pcs)
        spec.set_peaks(self.peaks)
        return spec

class PeakMap(object):

    def __init__(self, spectra, meta=dict()):
        self.spectra = spectra
        self.meta = meta

    def filter(self, condition):
        return PeakMap([s for s in self.spectra if condition(s)], self.meta)

    @classmethod
    def fromMSExperiment(clz, mse):
        assert type(mse) ==pyOpenMS.MSExperiment
        specs = [ Spectrum.fromMSSpectrum(mse[i]) for i in range(mse.size()) ]
        meta = dict()
        meta["source"] = mse.getLoadedFilePath().c_str()
        return clz(specs, meta) 

    def __len__(self):
        return len(self.spectra)

    def __iter__(self):
        return iter(self.spectra)

    def toMSExperiment(self):
        exp = pyOpenMS.MSExperiment()
        for spec in self.spectra:
            exp.push_back(spec.toMSSpectrum())
        exp.updateRanges()
        exp.setLoadedFilePath(pyOpenMS.String(self.meta.get("source","")))
        return exp

    def __getitem__(self, idx):
        return self.spectra[idx]
        

    
