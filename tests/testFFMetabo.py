
def test_ffm():
    import ms
    pm = ms.loadPeakMap("data/test.mzXML")
    pm = pm.extract(rtmin=6, rtmax=12, mzmin=350, mzmax=400)

    ftab = ms.metaboFeatureFinder(pm)
    assert len(ftab) == 19, len(ftab)
    ftab.print_()

    ftab2 = ms.metaboFeatureFinder(pm, "std")
    assert len(ftab2) == 30, len(ftab2)
    ftab2.print_()

    ftab2 = ms.metaboFeatureFinder(pm, ms_level=1)
    assert len(ftab2) == 19, len(ftab2)
    ftab2.print_()

    al1, al2 = ms.rtAlign([ftab2, ftab2], refTable=ftab2, destination=".")


