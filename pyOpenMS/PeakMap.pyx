from MSSpectrum cimport *
from MSExperiment cimport *
from ChromatogramPeak cimport *
from Peak1D cimport *

from PeakMap import PeakMap


cdef OpenMsPeakMapToPy(MSExperiment[Peak1D, ChromatogramPeak] map_):
        peakMap = PeakMap()
        peakMap.specs = [ OpenMsSpecToPy(map_[i]) for i in range(map_.size()) ]
        return peakMap
       
cdef MSExperiment[Peak1D, ChromatogramPeak] OpenMsPeakMapFromPy(peakmap):
        assert isinstance(peakmap, PeakMap)
        cdef MSExperiment[Peak1D, ChromatogramPeak] peakmap_
        for s in peakmap.specs:
            peakmap_.push_back(OpenMsSpecFromPy(s)) 
        peakmap_.updateRanges()
        return peakmap_
        

