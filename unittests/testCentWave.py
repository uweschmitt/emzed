import libms
import ms

def testCentwaveFeatureDetector():

    print "load"
    ds = ms.loadPeakMap("data/test.mzXML")
    print "loaded"
    det = libms.RConnect.CentwaveFeatureDetector(ppm=3, peakwidth=(8, 13), snthresh=40, prefilter=(8, 10000), mzdiff=1.5 )
    assert det.__doc__ != None
    table = det.process(ds)
    assert len(table) == 17, len(table)
    assert len(table.colNames) ==  13
    assert len(table.colTypes) ==  13
    
