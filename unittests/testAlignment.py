from libms.Alignment import *
import ms

def testPoseClustering():
    pm = ms.loadPeakMap("data\SHOrt_MS2_FILE.mzData")
    maps = alignPeakMapsWithPoseClustering([pm, pm])
    assert len(maps)==2
    assert len(maps[0]) == len(pm)
    assert len(maps[1]) == len(pm)
    for s1, s2, sorig in zip(maps[0], maps[1], pm):
        assert abs(s1.rt-sorig.rt)<1e-3
        assert abs(s2.rt-sorig.rt)<1e-3
    
