import ms
from   pyOpenMS import *
import os.path as osp

def testLoadMap():
    from_ = "data/SHORT_MS2_FILE.mzXML"
    ds = ms.loadExperiment(from_)
    assert ds.getMetaValue(String("source")).toString() == osp.basename(from_)

    ms.storeExperiment(ds, "temp_output/utilstest.mzML")
    ds = ms.loadExperiment("temp_output/utilstest.mzML")

    ms.storeExperiment(ds, "temp_output/utilstest.mzData")
    ds = ms.loadExperiment("temp_output/utilstest.mzData")
