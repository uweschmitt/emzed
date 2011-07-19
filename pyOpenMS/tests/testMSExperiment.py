
import sys
sys.path.insert(0, "..")
from pyOpenMS import *

def test_loadMzXMLFile():
    msExp = loadMzXMLFile("tests\\data\\READW_MS2_dataset.mzXML")
    #msExp = loadMzXMLFile("tests\\data\\X2XML_MS_dataset.mzXML")
    assert msExp != None

    assert len(msExp) == 2005 # 2884 # 2005
    print len(msExp)
    
    spec0 = msExp[0]
    print len(spec0)
    print len(msExp[1])
    settings = spec0.getInstrumentSettings()
    print settings.getPolarity()

    spec0 = msExp[11]
    print len(spec0)
    print spec0.findNearest(1000)
    for k in range(len(spec0)):
        print k, spec0[k]

    print spec0.getPrecursors()


    msExp.sortSpectraByRT()
