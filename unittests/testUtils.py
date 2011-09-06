import utils, libms

def testLoadMap():
    ds = utils.loadMap("data\SHORT_MS2_FILE.mzXML")

    libms.saveMzMlFile(ds, "temp_output/utilstest.mzML")
    ds = utils.loadMap("temp_output/utilstest.mzML")

    libms.saveMzDataFile(ds, "temp_output/utilstest.mzData")
    ds = utils.loadMap("temp_output/utilstest.mzData")
