from libms.DataStructures.MSTypes import *
from pyOpenMS import *
import numpy as np
import os.path

class TestMSTypes(object):

    def test001(self):
        exp = MSExperiment()
        basename = "SHORT_MS2_FILE.mzData"
        FileHandler().loadExperiment(os.path.join("data", basename), exp)
        assert exp.size()>0

        pc = Precursor()
        pc.setMZ(1.0)
        pc.setIntensity(100)
        s0 = exp[0]
        s0.setPrecursors([pc])
        spec = Spectrum.fromMSSpectrum(s0)
        settings = InstrumentSettings()
        settings.setPolarity(Polarity.POSITIVE)
        s0.setInstrumentSettings(settings)

        self.compare_specs(spec, s0)

        specneu = Spectrum.fromMSSpectrum(spec.toMSSpectrum())

        self.compare_specs(specneu, s0)

        pm = PeakMap.fromMSExperiment(exp)
        assert os.path.basename(pm.meta["source"]) ==  basename

        self.compare_exp(pm, exp, basename)
        pm2 = PeakMap.fromMSExperiment(pm.toMSExperiment())
        self.compare_exp(pm2, exp, basename)

    def compare_exp(self, pm, exp, basename):

        assert len(pm) == exp.size()

        assert (pm.spectra[0].rt-exp[0].getRT())/exp[0].getRT() < 1e-7
        assert pm.spectra[0].msLevel == exp[0].getMSLevel()
        assert pm.spectra[0].peaks.shape == (exp[0].size(), 2)

    def compare_specs(self, spec, s0):

        assert (spec.rt-s0.getRT())/s0.getRT() < 1e-7
        assert spec.msLevel == s0.getMSLevel()
        assert spec.peaks.shape == (s0.size(), 2)
        assert spec.precursors == [ (1.0, 100) ], spec.precursors
        assert spec.polarity == "+"

        assert len(spec) == s0.size() 


    def testIntensityInRange(self):
        data = np.array([ 0.0, 1.0, 2.0, 3.0, 4.0, 5.0 ]).reshape(-1,1)
        ones = np.ones_like(data)
        peaks = np.hstack((data, ones))
        assert peaks.shape == (6,2)
        spec = Spectrum(peaks, 0.0, 1, "0")
        assert spec.intensityInRange(0.0, 5.0) == 6.0
        assert spec.intensityInRange(0.1, 5.0) == 5.0
        assert spec.intensityInRange(0.0, 4.5) == 5.0
        assert spec.intensityInRange(0.5, 4.5) == 4.0
        assert spec.intensityInRange(2.0, 2.0) == 1.0
        assert spec.intensityInRange(2.1, 2.0) == 0.0
