import pyOpenMS
import numpy as np
import os.path
import copy


class Spectrum(object):

    def __init__(self, peaks, rt, msLevel, polarity, precursors=[]):
        assert type(peaks) == np.ndarray, type(peaks)
        assert polarity in "0+-", "polarity must be +, - or 0"
        self.rt = rt
        self.msLevel = msLevel
        self.precursors = precursors
        self.polarity = polarity
        peaks = peaks[peaks[:,1]>0] # remove zero intensities
        # sort resp. mz values:
        perm = np.argsort(peaks[:,0])
        self.peaks = peaks[perm,:]

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
        return self.peaksInRange(mzmin, mzmax)[:,1].sum()

    def peaksInRange(self, mzmin=None, mzmax=None):
        if mzmin is None and mzmax is None:
            raise Exception("no limits provided. need mzmin or mzmax")
        if mzmin is not None:
            imin = self.peaks[:,0].searchsorted(mzmin)
        else:
            imin = 0
        if mzmax is not None:
            imax = self.peaks[:,0].searchsorted(mzmax, side='right')
        else:
            # exclusive:
            imax = self.peaks.shape[0]
        return self.peaks[imin:imax]

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

    """ This is the container object for spectra of type :ref:Spectrum.
        Peakmaps can be loaded from .mzML, .mxXML or .mzData files,
        using :py:func:`~ms.loadPeakMap`
    """
 

    def __init__(self, spectra, meta=dict()):
        self.spectra = spectra
        """ attribute spectra is a list of objects of type 
            :py:class:`~.Spectrum` """
        self.meta = meta
        polarities = set(spec.polarity for spec in spectra)
        if len(polarities) > 1:
            print
            print "INCONSISTENT POLARITIES"
            for i, s in enumerate(spectra):
                print "%7.2fm : %s" % (s.rt/60.0, s.polarity),
                if i%5==4:
                    print
            print
        elif len(polarities)==1:
            self.polarity = polarities.pop()
        else:
            self.polarity = None

    def extract(self, rtmin=None, rtmax=None, mzmin=None, mzmax=None):
        """
        returns restricted Peakmap with given limits.
        Parameters with *None* value are not considered.

        Examples::

            pm.extract(rtmax = 12.5 * 60)
            pm.extract(rtmin = 12*60, rtmax = 12.5 * 60)
            pm.extract(rtmax = 12.5 * 60, mzmin = 100, mzmax = 200)
            pm.extract(rtmin = 12.5 * 60, mzmax = 200)
            pm.extract(mzmax = 200)

        \ 
        """
        spectra = copy.deepcopy(self.spectra)
        if rtmin:
            spectra = [ s for s in spectra if rtmin <= s.rt ]
        if rtmax:
            spectra = [ s for s in spectra if rtmax >= s.rt ]

        if mzmin is not None or mzmax is not None:
            for s in spectra:
                s.peaks = s.peaksInRange(mzmin, mzmax)

        return PeakMap(spectra, self.meta.copy())


    def filter(self, condition):
        """ builds new peakmap where ``condition(s)`` is ``True`` for
            spectra ``s`
        """
        return PeakMap([s for s in self.spectra if condition(s)], self.meta)

    def specsInRange(self, rtmin, rtmax):
        """
        returns list of spectra with rt values in range ``rtmin...rtmax``
        """
        return [spec for spec in self.spectra if rtmin <= spec.rt <= rtmax]

    def levelOneSpecsInRange(self, rtmin, rtmax):
        """
        returns lists level one spectra in peakmap
        """
        # rt values can be truncated/rounded from gui or other sources,
        # so wie dither the limits a bit, spaces in realistic rt values
        # are much higher thae 1e-2 seconds
        return [spec for spec in self.spectra if rtmin-1e-2 <= spec.rt <= rtmax+1e-2
                                             and spec.msLevel == 1]

    def chromatogram(self, mzmin, mzmax, rtmin=None, rtmax=None):
        """
        extracts chromatorgram in given rt- and mz-window.
        returns a tuple ``(rts, intensities)`` where ``rts`` is a list of
        rt values (in seconds, as allways)  and ``intensities`` is a 
        list of same lenght containing the summed up peaks for each
        rt value.
        """
        if not self.spectra:
            return [], []
        if rtmin is None:
            rtmin = self.spectra[0].rt
        if rtmax is None:
            rtmax = self.spectra[-1].rt
        specs = self.levelOneSpecsInRange(rtmin, rtmax)
        rts = [s.rt for s in specs]
        intensities = [s.intensityInRange(mzmin, mzmax) for s in specs]
        return rts, intensities

    def ms1Peaks(self, rtmin=None, rtmax=None):
        if rtmin is None:
            rtmin = self.spectra[0].rt
        if rtmax is None:
            rtmax = self.spectra[-1].rt
        specs = self.levelOneSpecsInRange(rtmin, rtmax)
        # following vstack does not like empty sequence, so:
        if len(specs):
            peaks = np.vstack([s.peaks for s in specs])
            perm = np.argsort(peaks[:,0])
            return peaks[perm,:]
        return np.zeros((0,2), dtype=float)

    def allRts(self):
        return [spec.rt for spec in self.spectra]

    def levelOneRts(self):
        return [spec.rt for spec in self.spectra if spec.msLevel == 1]

    def levelNSpecs(self, minN, maxN):
        return [spec for spec in self.spectra if minN <= spec.msLevel <= maxN]

    def shiftRt(self, delta):
        for spec in self.spectra:
            spec.rt += delta
        return self

    def mzRange(self):
        """ returns mz-range *(mzmin, mzmax)* of current peakmap """
        mzmin = min(s.peaks[:, 0].min() for s in self.spectra if len(s.peaks))
        mzmax = max(s.peaks[:, 0].max() for s in self.spectra if len(s.peaks))
        return float(mzmin), float(mzmax)

    def rtRange(self):
        """ returns rt-range *(rtmin, tax)* of current peakmap """
        rtmin = self.spectra[0].rt if len(self.spectra) else 1e300
        rtmax = self.spectra[-1].rt if len(self.spectra) else -1e300
        return rtmin, rtmax


    @classmethod
    def fromMSExperiment(clz, mse):
        assert type(mse) ==pyOpenMS.MSExperiment
        specs = [ Spectrum.fromMSSpectrum(mse[i]) for i in range(mse.size()) ]
        meta = dict()
        meta["full_source"] = mse.getLoadedFilePath().c_str()
        meta["source"] = os.path.basename(meta.get("full_source"))
        return clz(specs, meta)

    def __len__(self):
        return len(self.spectra)

    def toMSExperiment(self):
        exp = pyOpenMS.MSExperiment()
        for spec in self.spectra:
            exp.push_back(spec.toMSSpectrum())
        exp.updateRanges()
        exp.setLoadedFilePath(pyOpenMS.String(self.meta.get("source","")))
        return exp
