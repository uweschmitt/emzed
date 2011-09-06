import ms

def testLoadMap():
    ds = ms.loadMap("data\SHORT_MS2_FILE.mzXML")

    ms.saveMzMlFile(ds, "temp_output/utilstest.mzML")
    ds = ms.loadMap("temp_output/utilstest.mzML")

    ms.saveMzDataFile(ds, "temp_output/utilstest.mzData")
    ds = ms.loadMap("temp_output/utilstest.mzData")
