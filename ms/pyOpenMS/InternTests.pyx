import numpy as np


def testParam():
    orig = { "a":3, "b":2.0, "c":3L, "d:e" : "uwe" }
    cdef Param p = dictToParam( orig)
    cdef string * name = new string("uwe.ini")
    p.store(deref(name))
    back = paramToDict(p)
    assert back==orig

def testSpectrum():
    spec = Spectrum( 1.23, [ (0,1) ], ( "+", 1, [ (700.1, 100) ] ) )
    back = OpenMsSpecToPy(OpenMsSpecFromPy(spec))
    assert np.all(spec.peaks == back.peaks)
    assert spec.polarization == back.polarization
    assert spec.msLevel == back.msLevel
    assert spec.RT == back.RT
    assert spec.precursors == back.precursors
    
  
def testPeakMap():
    
    spec = Spectrum( 0.1, [ (0,3) ], ( "+", 1, [ (700.2, 200) ] ) )
    spec1= Spectrum( 0.2, [ (1,1) ], ( "+", 1, [] ) )
    pm = PeakMap([spec, spec1])
    cdef MSExperiment[Peak1D, ChromatogramPeak] pm_ = OpenMsPeakMapFromPy(pm)
    pm_.updateRanges()
    back = OpenMsPeakMapToPy(pm_)
    assert len(back.specs) == len(pm.specs)
    assert back.specs[0].RT == pm.specs[0].RT
    assert back.specs[1].RT == pm.specs[1].RT
    assert back.specs[0].polarization == pm.specs[0].polarization
    assert back.specs[1].polarization == pm.specs[1].polarization
    assert back.specs[0].msLevel == pm.specs[0].msLevel
    assert back.specs[1].msLevel == pm.specs[1].msLevel
    assert np.all(back.specs[0].peaks == pm.specs[0].peaks)
    assert np.all(back.specs[1].peaks == pm.specs[1].peaks)
    assert back.specs[0].precursors == pm.specs[0].precursors
    assert back.specs[1].precursors == pm.specs[1].precursors
    
    
def testFeature():
    feat = Feature(1.0, 2.0)
    back = OpenMsFeatureToPy(OpenMsFeatureFromPy(feat))
    assert feat.MZ == back.MZ
    assert feat.RT == back.RT

def testFeatureMap():
    feat1 = Feature(1.0, 2.0)
    feat2 = Feature(3.0, 4.0)
    fm = FeatureMap([feat1, feat2])
    back = OpenMsFeatureMapToPy(OpenMsFeatureMapFromPy(fm))
    assert len(fm.features) == len(back.features)
    for f1, f2 in zip (fm.features, back.features):
        assert f1.RT == f2.RT
        assert f1.MZ == f2.MZ

def run_tests():
    testParam()
    testSpectrum()
    testPeakMap()
    testFeature()
    testFeatureMap()
    return True
    
    
    
        
