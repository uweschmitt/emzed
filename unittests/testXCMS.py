import sys
sys.path.insert(0, "..")
from pyOpenMS import *
from RConnect import *

def testFeatureDetector():
    ds = loadMzXmlFile("data/test.mzXML")
    table = XCMSPeakDetector(ds)
    assert len(table) == 44
    assert len(table.colNames) ==  13
    assert len(table.colTypes) ==  13
    assert set(table.colNames) == set(XCMSFeatureParser.headlines[0].split() )
    
    
