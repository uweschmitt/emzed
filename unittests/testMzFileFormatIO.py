
import sys
sys.path.insert(0, "..")

from pyOpenMS import *

def test_loadMzXMLFile():
    saveMzXmlFile(loadMzDataFile("data/SHORT_MS2_FILE.mzData"), "temp_output/short.mzXML")
    msExp = loadMzXmlFile("temp_output/short.mzXML")

    assert msExp != None

    assert len(msExp) == 41 
    
    spec0 = msExp.specs[0]
    assert spec0.id=="scan=1"
    assert spec0.polarization == "+"
    assert spec0.precursors == []
    assert spec0.msLevel == 1
    assert len(spec0) == 21


    spec0 = msExp.specs[40]
    assert spec0.id=="scan=41"
    assert spec0.polarization == "+"
    assert len(spec0.precursors) == 1
    assert len(spec0.precursors[0]) == 2
    assert spec0.msLevel == 2
    assert len(spec0) == 121 


def test_loadMzMLFile():
    saveMzMlFile(loadMzDataFile("data/SHORT_MS2_FILE.mzData"), "temp_output/short.mzML")
    msExp = loadMzMlFile("temp_output/short.mzML")

    assert msExp != None

    assert len(msExp) == 41 
    
    spec0 = msExp.specs[0]
    assert spec0.id=="spectrum=1"
    assert spec0.polarization == "+"
    assert spec0.precursors == []
    assert spec0.msLevel == 1
    assert len(spec0) == 21


    spec0 = msExp.specs[40]
    assert spec0.id=="spectrum=41"
    assert spec0.polarization == "+"
    assert len(spec0.precursors) == 1
    assert len(spec0.precursors[0]) == 2
    assert spec0.msLevel == 2
    assert len(spec0) == 121 

def test_loadMzDataFile():
    saveMzDataFile(loadMzDataFile("data/SHORT_MS2_FILE.mzData"), "temp_output/short.mzData")
    msExp =loadMzDataFile("temp_output/short.mzData")

    assert msExp != None

    assert len(msExp) == 41 
    
    spec0 = msExp.specs[0]
    assert spec0.id=="spectrum=1"
    assert spec0.polarization == "+"
    assert spec0.precursors == []
    assert spec0.msLevel == 1
    assert len(spec0) == 21


    spec0 = msExp.specs[40]
    assert spec0.id=="spectrum=41"
    assert spec0.polarization == "+"
    assert len(spec0.precursors) == 1
    assert len(spec0.precursors[0]) == 2
    assert spec0.msLevel == 2
    assert len(spec0) == 121 
