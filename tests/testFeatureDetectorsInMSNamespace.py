import ms
import glob
import os

def testRunCentwave():

    pm = ms.loadPeakMap("data/test.mzXML")
    table = ms.runCentwave(pm)
    #runCentwave("data/test.mzXML", destination="temp_output", configid="std")
    #assert len(glob.glob("temp_output/test.csv")) == 1
    ##assert len(tables) == 1
    #table=tables[0]
    assert len(table) == 0, len(table)
    assert len(table.colNames) ==  16, len(table.colNames)
    assert len(table.colTypes) ==  16

def testMatcheFilter():

    pm = ms.loadPeakMap("data/test.mzXML")
    table = ms.runMatchedFilters(pm)

    assert len(table) == 742, len(table)
    assert len(table.colNames) ==  18, len(table.colNames)
    assert len(table.colTypes) ==  18
