from pyOpenMS import *
from RConnect import *

def testFeatureDetector():
    ds = loadMzXmlFile("data/short_100scans.mzXml")
    table = XCMSPeakDetector(ds)
    assert len(table) == 44
    

