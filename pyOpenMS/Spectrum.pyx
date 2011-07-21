from MSSpectrum cimport *
from Peak1D cimport *

from Spectrum import Spectrum


cdef vector[Peak1D] OpenMSPeaksFromPy(peaks):
        cdef vector[Peak1D] rv
        cdef Peak1D p
        for (mz, I) in peaks:
            p.setMZ(mz)
            p.setIntensity(I)
            rv.push_back(p)
        return rv

cdef OpenMsSpecToPy(MSSpectrum[Peak1D] spec_):
        spec = Spectrum()
        spec.peaks = [ ( spec_[i].getMZ(), spec_[i].getIntensity()) for i in range(spec_.size()) ]
        spec.polarization = "0+-"[spec_.getInstrumentSettings().getPolarity()]
        spec.msLevel = spec_.getMSLevel()
        spec.RT = spec_.getRT()
        return spec
       
cdef MSSpectrum[Peak1D] OpenMsSpecFromPy(spec):
        assert isinstance(spec, Spectrum)
        cdef MSSpectrum[Peak1D] spec_
        cdef vector[Peak1D] peaksVec = OpenMSPeaksFromPy(spec.peaks)
        spec_.assign(peaksVec.begin(), peaksVec.end())
        cdef int code = int({ "0" : 0, "+" : 1, "-" : 2 } [spec.polarization])
        spec_.getInstrumentSettings().setPolarity(<Polarity> code)
        spec_.setMSLevel(spec.msLevel)
        spec_.setRT(spec.RT)
        spec_.updateRanges()
        return spec_
        

def test():
    spec = Spectrum( ([ (0,1) ], "+", 1) )
    back = OpenMsSpecToPy(OpenMsSpecFromPy(spec))
    assert spec.peaks == back.peaks
    assert spec.polarization == back.polarization
    assert spec.msLevel == back.msLevel
    
    

    
    
