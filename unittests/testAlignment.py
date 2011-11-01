from libms.Alignment import *
import ms

def testPoseClustering():
    pm = ms.loadPeakMap("data\SHOrt_MS2_FILE.mzData")
    maps = alignPeakMapsWithPoseClustering([pm, pm], max_num_peaks_considered=-1)
    assert len(maps)==2
    assert len(maps[0]) == len(pm)
    assert len(maps[1]) == len(pm)
    for s1, s2, sorig in zip(maps[0], maps[1], pm):
        assert abs(s1.rt-sorig.rt)<1e-3
        assert abs(s2.rt-sorig.rt)<1e-3
    
def testSpectrumAlignment():
    pm = ms.loadPeakMap("data\SHOrt_MS2_FILE.mzData")
    maps = alignPeakMapsWithSpectrumAlignment([pm, pm], gapcost=float(1),
                                              affinegapcost=float(0.5),
                                              scorefunction="s", 
                                              showProgress=True)
    assert len(maps)==2
    assert len(maps[0]) == len(pm)
    assert len(maps[1]) == len(pm)
    for s1, s2, sorig in zip(maps[0], maps[1], pm):
        assert abs(s1.rt-sorig.rt)<1e-3
        assert abs(s2.rt-sorig.rt)<1e-3
    
