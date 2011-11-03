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
    
