from libms.Alignment import *
import ms
import os
import pickle
import numpy as np

def testPoseClustering():
    ft=pickle.load(open("data/ft.pickled","rb"))
    irt = ft.getIndex("rt")
    before = np.array([ r[irt] for r in ft.rows])
    ms.alignFeatureTables([ft,ft], ".")
    irt = ft.getIndex("rt")
    after = np.array([ r[irt] for r in ft.rows])

    # aligning against itself should do something:
    assert np.any(before!=after)
    # ... but not too much:
    assert np.linalg.norm(before-after)<1e-3 
    
    # alignmen should produce alignment map:
    assert os.path.exists("zeros_aligned.png")
    
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
    
