
def test_ffm():
    import ms
    pm = ms.loadPeakMap("data/test.mzXML")
    pm = pm.extract(rtmin=6, rtmax=12, mzmin=350, mzmax=400)
    ftab = ms.metaboFeatureFinder(pm)
    assert len(ftab) == 19
    ftab = ms.metaboFeatureFinder(pm, "std")
    assert len(ftab) == 30, len(ftab)
