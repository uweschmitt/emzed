import ms
import batches
import glob
import os

def testPeakPickerHiRes():

    inPath  = "gauss_data.mzML"
    outPath = "temp_output/gauss_data_centroided.mzML"
    try:
        os.remove(outPath)
    except:
        pass
    batches.runPeakPickerHiRes(inPath, destination="temp_output", configid="std")
    assert len(glob.glob(outPath)) == 1
        

def testRunCentwave():

    try:
        os.remove("temp_output/test.csv")
    except:
        pass
    tables = batches.runCentwave("data/test.mzXML", destination="temp_output", configid="std")
    assert len(glob.glob("temp_output/test.csv")) == 1
    assert len(tables) == 1
    table=tables[0]
    assert len(table) == 0, len(table)
    assert len(table.colNames) ==  11, len(table.colNames)
    assert len(table.colTypes) ==  11
    
def testMatcheFilter():

    try:
        os.remove("temp_output/test.csv")
    except:
        pass
    tables = batches.runMatchedFilter("data/test.mzXML", destination="temp_output", configid="std")
    assert len(glob.glob("temp_output/test.csv")) == 1
    assert len(tables) == 1
    table=tables[0]
    assert len(table) == 742, len(table)
    assert len(table.colNames) ==  13, len(table.colNames)
    assert len(table.colTypes) ==  13
