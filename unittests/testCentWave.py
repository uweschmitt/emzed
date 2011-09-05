import ms

def testCentwaveFeatureDetector():

    ds = ms.loadMzXmlFile("data/test.mzXML")
    det = ms.CentWaveFeatureDetector(ppm=3, peakwidth=(8, 13), snthresh=40, prefilter=(8, 10000), mzdiff=1.5 )
    assert det.__doc__ != None
    table = det.process(ds)
    assert len(table) == 17, len(table)
    assert len(table.colNames) ==  11
    assert len(table.colTypes) ==  11
    
