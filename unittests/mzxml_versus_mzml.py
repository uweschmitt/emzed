import sys
sys.path.insert(0, "..")
from pyOpenMS import *
#from RConnect import *

def _x_testFeatureDetector():
    #ds = loadMzXmlFile("data/short_100scans.mzXml")
    ds = loadMzXmlFile("data/test.mzXML")
    print "check sorted after load :", 
    ds.testSorted()
    print
    table = XCMSPeakDetector(ds)
    assert len(table) == 44
    assert len(table.colNames) ==  13
    assert len(table.colTypes) ==  13
    assert set(table.colNames) == set(XCMSFeatureParser.headlines[0].split() )
    
    
def testMzML():

    print "load mzxml"
    ds = loadMzXmlFile("data/test.mzXML", False, False)
    
    print "test if loaded data is sorted:",
    print ds.testSorted()

    print "save as mzml"
    saveMzMlFile(ds, "t.mzML")
    print "load mzml"
    ds = loadMzMlFile("t.mzML", False, False)
    print "test if still sorted:",
    print ds.testSorted()


def testMzXML():

    print "load mzxml"
    ds = loadMzXmlFile("data/test.mzXML", False, False)
    
    print "test if loaded data is sorted:",
    print ds.testSorted()


    print "save as mzxml"
    saveMzXmlFile(ds, "t.mzXML")
    print "load mzxml"
    ds = loadMzXmlFile("t.mzXML", False, False)
    print "test if still sorted:",
    print ds.testSorted()
    print
    print "sort !"
    ds.sortByMz()

    print "save as mzxml"
    saveMzXmlFile(ds, "t.mzXML")
    print "load mzxml"
    ds = loadMzXmlFile("t.mzXML", False, False)
    print "test if still sorted:",
    print ds.testSorted()


if __name__ == "__main__":
    testMzML()
    print 

    testMzXML()
    print 
