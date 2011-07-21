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
        RT = spec_.getRT()
        peaks = [ ( spec_[i].getMZ(), spec_[i].getIntensity()) for i in range(spec_.size()) ]
        polarization = "0+-"[spec_.getInstrumentSettings().getPolarity()]
        msLevel = spec_.getMSLevel()
        cdef vector[Precursor] pcs_ = spec_.getPrecursors()
        cdef pcs = []
        for i in range(pcs_.size()):
            pcs.append((pcs_[i].getMZ(), pcs_[i].getIntensity()))
        return Spectrum(RT, peaks, (polarization, msLevel, pcs))
       
cdef MSSpectrum[Peak1D] OpenMsSpecFromPy(spec):
        assert isinstance(spec, Spectrum)
        cdef MSSpectrum[Peak1D] spec_
        cdef vector[Peak1D] peaksVec = OpenMSPeaksFromPy(spec.peaks)
        spec_.assign(peaksVec.begin(), peaksVec.end())
        cdef int code = int({ "0" : 0, "+" : 1, "-" : 2 } [spec.polarization])
        spec_.getInstrumentSettings().setPolarity(<Polarity> code)
        spec_.setMSLevel(spec.msLevel)
        spec_.setRT(spec.RT)
        cdef vector[Precursor] pcs 
        cdef Precursor * pc
        for (mz, I) in spec.precursors:
            pc = new Precursor()
            pc.setMZ(mz)
            pc.setIntensity(I)
            pcs.push_back(deref(pc))
            del pc

        spec_.setPrecursors(pcs)
        spec_.updateRanges()
        return spec_
        

    

    
    
