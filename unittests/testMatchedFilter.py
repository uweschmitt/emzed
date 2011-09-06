import libms

    
    
def testMatchedFilterFeatureDetector():

    ds = libms.loadMzXmlFile("data/test.mzXML")
    det = libms.MatchedFilterFeatureDetector()
    assert det.__doc__ != None
    table = det.process(ds)
    assert len(table) == 742, len(table)
    assert len(table.colNames) ==  13, len(table.colNames)
    assert len(table.colTypes) ==  13
    
