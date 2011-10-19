import ms
import os.path as osp

def testLoadMap():
    from_ = "data/SHORT_MS2_FILE.mzXML"
    ds = ms.loadPeakMap(from_)
        
    assert osp.basename(ds.meta.get("source")) ==  osp.basename(from_)

    ms.storePeakMap(ds, "temp_output/utilstest.mzML")
    ds2 = ms.loadPeakMap("temp_output/utilstest.mzML")

    assert len(ds)==len(ds2)

    ms.storePeakMap(ds2, "temp_output/utilstest.mzData")
    ds3 = ms.loadPeakMap("temp_output/utilstest.mzData")

    assert len(ds)==len(ds3)
