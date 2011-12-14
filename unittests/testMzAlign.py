import ms
import glob

def testMzAlign():
    tab = ms.loadTable("data/ftab_for_mzalign.table")
    before = tab.mz.values
    pm = tab.peakmap.values[0]
    s0 = pm.spectra[0].peaks[:,0]
    ms.mzalign(tab, interactive=False, minPoints=4, tol=14*MMU, destination="temp_output")
    after = tab.mz.values
    pm = tab.peakmap.values[0]
    s0 = pm.spectra[0].peaks[:,0]
    assert abs(s0[0]-202.121231079) < 1e-5, float(s0[0])
    assert abs(after[0]-272.199238673) < 1e-5, float(after[0])

    assert len(glob.glob("temp_output/2011-10-06_054_PKTB*"))==4
