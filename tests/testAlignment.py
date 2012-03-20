import ms
import os
import numpy as np
import copy

def testPoseClustering():
    ft = ms.loadTable("data/features.table")
    irt = ft.getIndex("rt")

    # make copy and shift
    ft2=copy.deepcopy(ft)
    def shift(t, col):
        ix = t.getIndex(col)
        for r in t.rows:
            r[ix] += 2.0

    shift(ft2, "rt")
    shift(ft2, "rtmin")
    shift(ft2, "rtmax")

    pms = set(ft2.get(row, "peakmap") for row in ft2.rows)
    pmrtsbefore = []
    assert len(pms) == 1
    for pm in pms:
        for spec in pm.spectra:
            pmrtsbefore.append(spec.rt)
            spec.rt += 2.0

    # delete one row, so ft should become reference map !
    del ft2.rows[-1]

    ftneu, ft2neu = ms.rtAlign([ft,ft2], refTable=ft, destination="temp_output", nPeaks=9999,
                                          numBreakpoints=2)

    check(ft, ft2, ftneu, ft2neu)

    ft2neu, ftneu = ms.rtAlign([ft2,ft], refTable=ft, destination="temp_output", nPeaks=9999,
                                          numBreakpoints=2)

    check(ft, ft2, ftneu, ft2neu)

    ftneu, ft2neu = ms.rtAlign([ft,ft2], destination="temp_output", nPeaks=9999,
                                          numBreakpoints=2)

    check(ft, ft2, ftneu, ft2neu)



def check(ft, ft2, ftneu, ft2neu):
    def getrt(t, what):
        return  np.array([t.get(row, what) for row in t.rows])

    # refmap ft should not be changed:
    assert np.all(getrt(ftneu, "rt") == getrt(ft, "rt"))
    assert np.all(getrt(ftneu, "rtmin") == getrt(ft, "rtmin"))
    assert np.all(getrt(ftneu, "rtmax") == getrt(ft, "rtmax"))

    # but ft2 should:
    assert np.linalg.norm(getrt(ft2neu, "rt") - getrt(ft2, "rt")) >= 7.9
    assert np.linalg.norm(getrt(ft2neu, "rtmin") - getrt(ft2, "rtmin")) >= 7.9
    assert np.linalg.norm(getrt(ft2neu, "rtmax") - getrt(ft2, "rtmax")) >= 7.9

    # now ftneu and ft2neu should be very near.
    # remenber: ft2 has not as much rows as ft, so:
    assert np.linalg.norm(getrt(ft2neu, "rt") - getrt(ftneu, "rt")[:-1]) < 1e-6
    assert np.linalg.norm(getrt(ft2neu, "rtmin") - getrt(ftneu, "rtmin")[:-1]) < 1e-6
    assert np.linalg.norm(getrt(ft2neu, "rtmax") - getrt(ftneu, "rtmax")[:-1]) < 1e-6

    def getrtsfrompeakmap(table):
        pms = set(table.get(row, "peakmap") for row in table.rows)
        assert len(pms) == 1
        pm = pms.pop()
        return np.array([ spec.rt for spec in pm.spectra])

    assert np.linalg.norm(getrtsfrompeakmap(ft2neu)-getrtsfrompeakmap(ftneu))<1e-4

    ex = None
    try:
        ftneu, ft2neu = ms.rtAlign([ftneu,ft2neu], destination="temp_output", nPeaks=9999,
                                              numBreakpoints=2)
    except Exception, e:
        ex = e
    assert ex is not None, "aligning of aligned maps should not be possible"
    # alignmen should produce alignment map:
    assert os.path.exists("temp_output/test_aligned.png")



