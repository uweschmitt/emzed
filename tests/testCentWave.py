import libms
import ms

def testCentwaveFeatureDetector():

    print "load"
    ds = ms.loadPeakMap("data/test_mini.mzXML")
    print "loaded"
    det = libms.RConnect.CentwaveFeatureDetector(ppm=3, peakwidth=(8, 13), snthresh=40, prefilter=(8, 10000), mzdiff=1.5 )
    assert det.__doc__ != None
    table = det.process(ds)
    table.print_()
    assert len(table) == 1, len(table)

    assert len(table.getColNames()) ==  16, len(table.getColNames())
    assert len(table.getColTypes()) ==  16, len(table.getColTypes())
    assert "polarity" in table.getColNames()
