import ms
import glob
import os

def testRunCentwave():

    pm = ms.loadPeakMap("data/test_mini.mzXML")
    table = ms.runCentwave(pm,
                           ppm=3,
                           peakwidth=(8, 13),
                           snthresh=40,
                           prefilter=(8, 10000),
                           mzdiff=1.5 )
    #runCentwave("data/test.mzXML", destination="temp_output", configid="std")
    #assert len(glob.glob("temp_output/test.csv")) == 1
    ##assert len(tables) == 1
    #table=tables[0]
    assert len(table) == 1, len(table)
    assert len(table.getColNames()) ==  16, len(table.getColNames())
    assert len(table.getColTypes()) ==  16

def testMatchedFilter():

    pm = ms.loadPeakMap("data/test.mzXML")
    table = ms.runMatchedFilters(pm,
            destination="temp_output", configid="std", mzdiff=0, fwhm=50,
            steps=1, step=0.6)

    assert len(table) == 340, len(table)
    assert len(table.getColNames()) ==  18, len(table.getColNames())
    assert len(table.getColTypes()) ==  18
