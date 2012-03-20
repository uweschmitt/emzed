import libms.PeakPicking
import ms

def testPeakPicking():
    pp = libms.PeakPicking.PeakPickerHiRes()
    ds = ms.loadPeakMap("data/gauss_data.mzML")
    ds2 = pp.pickPeakMap(ds)
    assert len(ds) == len(ds2)
    assert ds2.spectra[0].peaks.shape == (9570, 2)
