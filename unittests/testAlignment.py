from libms.Alignment import *
import ms
import os
import pickle
import numpy as np
import copy

def testPoseClustering():
    ft = ms.loadTable("data/features.table")
    irt = ft.getIndex("rt")
    before = np.array([ r[irt] for r in ft.rows])

    # make copy and shift
    ft2=copy.deepcopy(ft)
    ix = ft2.getIndex("rt")
    for r in ft2.rows:
        r[ix] += 2.0
    # delete one row, so ft should become reference map !
    del ft2.rows[-1]

    ftneu, ft2neu = ms.alignFeatureTables([ft,ft2], "temp_output", nPeaks=9999,
                                          numBreakpoints=2)
    irt = ft.getIndex("rt")
    def getrt(t):
        return np.array([r[irt] for r in t.rows])

    # refmap ft should not be changed:
    assert np.all(getrt(ftneu) == getrt(ft))
    # but ft2 should:
    assert np.linalg.norm(getrt(ft2neu) - getrt(ft2)) >= 7.9

    # now ftneu and ft2neu should be very near.
    # remenber: ft2 has not as much rows as ft, so:
    assert np.linalg.norm(getrt(ft2neu) - getrt(ftneu)[:-1]) < 1e-6

    # alignmen should produce alignment map:
    assert os.path.exists("temp_output/test_aligned.png")

