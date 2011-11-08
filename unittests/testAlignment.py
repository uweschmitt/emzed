from libms.Alignment import *
import ms
import os
import pickle
import numpy as np

def testPoseClustering():
    ft=pickle.load(open("data/ft.pickled","rb"))
    irt = ft.getIndex("rt")
    before = np.array([ r[irt] for r in ft.rows])
    neu = ms.alignFeatureTables([ft,ft], ".", nPeaks=9999, numBreakpoints=2)

    assert len(neu) == 2
    irt = ft.getIndex("rt")

    after = np.array([ r[irt] for r in ft.rows])
    # args should not be changed !
    assert np.all(before==after)

    # result should be little aligned:
    for ft in neu:
        assert "aligned" in ft.meta
        after = np.array([ r[irt] for r in ft.rows])
        assert np.linalg.norm(before-after)<1e-3

    # alignmen should produce alignment map:
    assert os.path.exists("zeros_aligned.png")

