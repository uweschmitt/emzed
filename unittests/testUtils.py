import ms
from libms.pyOpenMS import *

def testLoadMap():
    ds = ms.loadMap("data\SHORT_MS2_FILE.mzXML")

    saveMzMlFile(ds, "temp_output/utilstest.mzML")
    ds = ms.loadMap("temp_output/utilstest.mzML")

    saveMzDataFile(ds, "temp_output/utilstest.mzData")
    ds = ms.loadMap("temp_output/utilstest.mzData")
