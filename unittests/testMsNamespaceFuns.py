import ms
import os.path as osp
import numpy as np
import copy


def testLoadMap():
    from_ = "data/SHORT_MS2_FILE.mzXML"
    ds = ms.loadPeakMap(from_)

    assert osp.basename(ds.meta.get("source")) ==  osp.basename(from_)

    ms.storePeakMap(ds, "temp_output/utilstest.mzML")
    ds2 = ms.loadPeakMap("temp_output/utilstest.mzML")

    assert len(ds)==len(ds2)

    ms.storePeakMap(ds2, "temp_output/utilstest.mzData")
    ds3 = ms.loadPeakMap("temp_output/utilstest.mzData")

    assert len(ds)==len(ds3)

def testAlignFeatureTables():
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
    assert osp.exists("temp_output/test_aligned.png")

def testIntegration():
    ft = ms.loadTable("data/features.table")
    ftr = ms.reintegrate(ft, "trapez")
    assert "area" in ftr.colNames
    assert "rmse" in ftr.colNames

