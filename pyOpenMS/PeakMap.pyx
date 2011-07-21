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
        

def test2():
    
    spec = Spectrum( ( 0.1, [ (0,3) ], "+", 1) )
    spec1 = Spectrum( ( 0.2, [ (1,1) ], "+", 1) )
    pm = PeakMap([spec, spec1])
    cdef MSExperiment[Peak1D, ChromatogramPeak] pm_ = OpenMsPeakMapFromPy(pm)
    pm_.updateRanges()
    back = OpenMsPeakMapToPy(pm_)
    assert len(back.specs) == len(pm.specs)
    assert back.specs[0].RT == pm.specs[0].RT
    assert back.specs[1].RT == pm.specs[1].RT
    assert back.specs[0].polarization == pm.specs[0].polarization
    assert back.specs[1].polarization == pm.specs[1].polarization
    assert back.specs[0].msLevel == pm.specs[0].msLevel
    assert back.specs[1].msLevel == pm.specs[1].msLevel
    assert back.specs[0].peaks == pm.specs[0].peaks
    assert back.specs[1].peaks == pm.specs[1].peaks
    
    

    
    
