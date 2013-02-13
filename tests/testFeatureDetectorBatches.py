import ms
import batches
import glob
import os

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
    assert len(table.getColNames()) ==  16, len(table.getColNames())
    assert len(table.getColTypes()) ==  16

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
    assert len(table.getColNames()) ==  18, len(table.getColNames())
    assert len(table.getColTypes()) ==  18
