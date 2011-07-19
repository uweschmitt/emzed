
import sys
sys.path.insert(0, "..")
from pyOpenMS import *

def test_loadMzXMLFile():
    msExp = loadMzXMLFile("tests\\data\\READW_MS2_dataset.mzXML")
    #msExp = loadMzXMLFile("tests\\data\\X2XML_MS_dataset.mzXML")
    assert msExp != None

    assert len(msExp) == 2005 # 2884 # 2005
    print len(msExp)
    
    settings = msExp[0].getInstrumentSettings()
    print settings.getPolarity()


    msExp.sortSpectraByRT()
