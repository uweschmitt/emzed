import ms
import libms

def testMatchedFilterFeatureDetector():

    print "load"
    ds = ms.loadPeakMap("data/test.mzXML")
    print "loaded"
    det = libms.RConnect.MatchedFilterFeatureDetector()
    assert det.__doc__ != None
    table = det.process(ds)
    print table.colNames
    assert len(table) == 742, len(table)
    assert len(table.colNames) ==  18, len(table.colNames)
    assert len(table.colTypes) ==  18
