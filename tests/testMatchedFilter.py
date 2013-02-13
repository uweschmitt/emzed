import ms
import libms

def testMatchedFilterFeatureDetector():

    print "load"
    ds = ms.loadPeakMap("data/test.mzXML")
    print "loaded"
    det = libms.RConnect.MatchedFilterFeatureDetector()
    assert det.__doc__ != None
    table = det.process(ds)
    print table.getColNames()
    assert len(table) == 742, len(table)
    assert len(table.getColNames()) ==  18, len(table.getColNames())
    assert len(table.getColTypes()) ==  18
