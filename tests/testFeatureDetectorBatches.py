import ms
import batches
import glob
import os

def testRunCentwave():

    try:
        os.remove("temp_output/test.csv")
    except:
        pass
    tables = batches.runCentwave("data/test_mini.mzXML",
                                 destination="temp_output",
                                 configid="std",
                                 ppm=3,
                                 peakwidth=(8, 13),
                                 snthresh=40,
                                 prefilter=(8, 10000),
                                 mzdiff=1.5 )
    assert len(glob.glob("temp_output/test_mini.csv")) == 1
    assert len(tables) == 1
    table=tables[0]
    assert len(table) == 1, len(table)
    assert len(table.getColNames()) ==  16, len(table.getColNames())
    assert len(table.getColTypes()) ==  16

def testMatchedFilter():

    try:
        os.remove("temp_output/test.csv")
    except:
        pass
    tables = batches.runMatchedFilter("data/test.mzXML",
            destination="temp_output", configid="std", mzdiff=0, fwhm=50,
            steps=1, step=0.6)
    assert len(glob.glob("temp_output/test.csv")) == 1
    table, = tables
    assert len(table) == 340, len(table)
    assert len(table.getColNames()) ==  18, len(table.getColNames())
    assert len(table.getColTypes()) ==  18
