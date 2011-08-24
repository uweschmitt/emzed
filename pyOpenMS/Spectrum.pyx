from pyOpenMS.pxd.MSSpectrum cimport *
from pyOpenMS.pxd.Peak1D cimport *
from pyOpenMS.pxd.string cimport *

cimport cpython

from Spectrum import Spectrum

import numpy as np
cimport numpy as np


cdef vector[Peak1D] OpenMSPeaksFromPy(np.ndarray[np.float32_t, ndim=2] peaks):
        cdef vector[Peak1D] rv
        cdef Peak1D p
        cdef float mz, I
        cdef int N
        N = peaks.shape[0]
        for i in range(N):
            mz = peaks[i,0]
            I  = peaks[i,1]
            p.setMZ(mz)
            p.setIntensity(I)
            rv.push_back(p)

        #for i in range(N-1):
            #if peaks[i,0]>peaks[i+1,0]:
                #print "py->openms: input peaks not sorted ", i
        #for i in range(N-1):
            ##if rv.at(i).getMZ() > rv.at(i+1).getMZ():
                #print "py->openms: output peaks not sorted ", i

        return rv

cdef OpenMsSpecToPy(MSSpectrum[Peak1D] spec_):

        cdef double RT = spec_.getRT()

        # this was the bottleneck !!!
        # peaks = [ ( spec_[i].getMZ(), spec_[i].getIntensity()) 
        #                           for i in range(spec_.size()) ]

        # now with numpy: MUCH faster (approx 10 times)
        cdef unsigned int n = spec_.size()
        cdef np.ndarray[np.float32_t, ndim=2] peaks 
        peaks = np.zeros( [n,2], dtype=np.float32)
        cdef Peak1D p
        for i in range(n):
            p = spec_[i]
            peaks[i,0] = p.getMZ()
            peaks[i,1] = p.getIntensity()

        #for i in range(n-1):
            #if peaks[i,0]>peaks[i+1,0]:
                #print "openms->py:   input peaks not sorted ", i
            #if spec_[i].getMZ() > spec_[i+1].getMZ():
                #print ">openms->py: output peaks not sorted ", i
        
        cdef int polix = spec_.getInstrumentSettings().getPolarity()
        cdef str polarization = "0+-"[polix]

        cdef int msLevel = spec_.getMSLevel()

        cdef vector[Precursor] pcs_ = spec_.getPrecursors()
        cdef pcs = []
        cdef unsigned int len_ = pcs_.size()
        for i in range(len_):
            pcs.append((pcs_[i].getMZ(), pcs_[i].getIntensity()))

        return Spectrum(RT, peaks, (polarization, msLevel, pcs, cpython.PyString_FromString(spec_.getNativeID().c_str())))
       
cdef MSSpectrum[Peak1D] OpenMsSpecFromPy(spec):

        assert isinstance(spec, Spectrum)

        cdef MSSpectrum[Peak1D] spec_


        cdef vector[Peak1D] peaksVec = OpenMSPeaksFromPy(spec.peaks)
        spec_.assign(peaksVec.begin(), peaksVec.end())

        cdef int code = int({ "0" : 0, "+" : 1, "-" : 2 } [spec.polarization])
        spec_.getInstrumentSettings().setPolarity(<Polarity> code)
        spec_.setMSLevel(spec.msLevel)
        spec_.setRT(spec.RT)
        
        cdef string * id = new string(spec.id)

        spec_.setNativeID(deref(id))

        del  id

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
       
def s2s(pm):
        return OpenMsSpecToPy(OpenMsSpecFromPy(pm))
