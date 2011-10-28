import ms
import batches
import glob
import os

def testPoseClustering():
    try:
        os.remove("temp_output/test.csv")
    except:
        pass
    
    batches.alignPeakMaps("data/SHORT*.mzData", destination="temp_output", 
                         npeaks=-1)

    assert len(glob.glob("temp_output/SHORT*aligned.mzML")) == 2
