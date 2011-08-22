from pyOpenMS import *
from RConnect import *

def testFeatureDetector():
    ds = loadMzXmlFile("data/short_100scans.mzXml")
    table = XCMSPeakDetector(ds)
    assert len(table) == 44
    assert len(table.colNames) ==  13
    assert len(table.colTypes) ==  13
    assert set(table.colNames) == set(XCMSFeatureParser.headlines[0].split() )
    
    

