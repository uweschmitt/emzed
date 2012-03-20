import os
import batches
import glob

def testPeakPickerHiRes():

    inPath  = "data/gauss_data.mzML"
    outPath = "temp_output/gauss_data_centroided.mzML"
    try:
        os.remove(outPath)
    except:
        pass
    batches.runPeakPickerHiRes(inPath, destination="temp_output", configid="std")
    assert len(glob.glob(outPath)) == 1

