
import sys
sys.path.insert(0, "..")
from pyOpenMS import *

def test_loadMzXMLFile():
    msExp = loadMzXmlFile("data/SHORT_MS2_FILE.mzXML")

    assert msExp != None

    assert len(msExp) == 41 # 2884 # 2005
    
    spec0 = msExp.specs[0]
    assert spec0.polarization == "+"
    assert spec0.precursors == []
    assert spec0.msLevel == 1
    assert len(spec0) == 61


    spec0 = msExp.specs[40]
    assert spec0.polarization == "+"
    assert len(spec0.precursors) == 1
    assert len(spec0.precursors[0]) == 2
    assert spec0.msLevel == 2
    assert len(spec0) == 305


