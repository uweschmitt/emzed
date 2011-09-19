
import configs, ms

def testPeakIntegration():
    integrator = dict(configs.peakIntegrators).get("std")
    assert len(str(integrator))>0

    ds = ms.loadMap("data/SHORT_MS2_FILE.mzData")
    integrator.setPeakMap(ds)

    rtmin = ds.specs[0].RT
    rtmax = ds.specs[30].RT

    print  rtmin, rtmax

    mzmin = ds.specs[0].peaks[10,0]
    mzmax = ds.specs[0].peaks[-10,0]

    result = integrator.integrate(mzmin, mzmax, rtmin, rtmax)
        
    area=result.get("area")
    rmse=result.get("rmse")

    assert abs(area-121858.8) < .1,  area
    assert abs(rmse-6904.9) < .1,  rmse
    
    integrator = dict(configs.peakIntegrators).get("asym_gauss")
    assert len(str(integrator))>0

    integrator.setPeakMap(ds)

    result = integrator.integrate(mzmin, mzmax, rtmin, rtmax)
        
    area=result.get("area")
    rmse=result.get("rmse")

    assert abs(area-29008.7) < .1,  area
    assert abs(rmse-7156.6) < .1,  rmse
