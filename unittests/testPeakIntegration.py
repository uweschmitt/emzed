
import configs, ms

def testPeakIntegration():
    integrator = configs.PeakIntegrators.get("std")
    assert isinstance(integrator.getInfo(), str)
    assert len(integrator.getInfo())>0

    ds = ms.loadMap("data/SHORT_MS2_FILE.mzData")
    integrator.setPeakMap(ds)

    rtmin = ds.specs[0].RT
    rtmax = ds.specs[30].RT

    mzmin = ds.specs[0].peaks[10,0]
    mzmax = ds.specs[0].peaks[-10,0]

    result = integrator.integrate(mzmin, mzmax, rtmin, rtmax)
        
    area=result.get("area")
    rmse=result.get("rmse")

    assert abs(area-118640.8) < .1,  area
    assert abs(rmse-6856.1) < .1,  rmse
    
    integrator = configs.PeakIntegrators.get("asym_gauss")
    assert isinstance(integrator.getInfo(), str)
    assert len(integrator.getInfo())>0

    integrator.setPeakMap(ds)

    result = integrator.integrate(mzmin, mzmax, rtmin, rtmax)
        
    area=result.get("area")
    rmse=result.get("rmse")

    assert abs(area-28764.6) < .1,  area
    assert abs(rmse-7146.1) < .1,  rmse
