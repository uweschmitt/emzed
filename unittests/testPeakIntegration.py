
import configs, ms
import numpy as np
from   libms.DataStructures import Spectrum, PeakMap

def run(integrator, areatobe, rmsetobe):
    assert len(str(integrator))>0

    try:
        ds = run.ds 
    except:
        ds = run.ds =  ms.loadPeakMap("data/SHORT_MS2_FILE.mzData")

    integrator.setPeakMap(ds)

    rtmin = ds.spectra[0].rt
    rtmax = ds.spectra[30].rt

    mzmin = ds.spectra[0].peaks[10,0]
    mzmax = ds.spectra[0].peaks[-10,0]

    result = integrator.integrate(mzmin, mzmax, rtmin, rtmax)
        
    area=result.get("area")
    rmse=result.get("rmse")

    print "area: is=%e  tobe=%e" % (area, areatobe)
    print "rmse: is=%e  tobe=%e" % (rmse, rmsetobe)

    assert abs(area-areatobe) < .1,  area
    assert abs(rmse-rmsetobe) < .1,  rmse

    params = result.get("params")

    rts = [ spec.rt for spec in ds.spectra ]

    x, y = integrator.getSmoothed(rts, params)

    return x,y, params

    #assert abs(area-121858.8) < .1,  area
    #assert abs(rmse-6904.9) < .1,  rmse

def testPeakIntegration():
    integrator = dict(configs.peakIntegrators).get("trapez")

    run(integrator,  134993.2, 0.0)

    integrator = dict(configs.peakIntegrators).get("std")
    run(integrator,  133996.0, 7586.0)

    
    integrator = dict(configs.peakIntegrators).get("asym_gauss")
    _, _, params = run(integrator, 32152.5, 8116.94)

    assert abs(params[0]- 39209.3) < 0.1, params[0]
    assert abs(params[1]- 0.1936) < 0.001, params[1]
    assert abs(params[2]- 0.18137) < 0.0001, params[2]
    assert abs(params[3]- 325.7) < 0.1, params[3]

def testTrapezIntegrationSimple():
       
    p0 = np.array((1.0, 1.0, 2.0, 2.0)).reshape(-1,2)
    p1 = np.array((2.0, 2.0, 3.0, 3.0)).reshape(-1,2)
    p2 = np.array((1.0, 1.0, 2.0, 2.0, 3.0, 3.0)).reshape(-1,2)
    p3 = np.array((3.0, 3.0)).reshape(-1,2)

    s0 = Spectrum(p0, 0.0, 1, '0')
    s1 = Spectrum(p1, 1.0, 1, '0')
    s2 = Spectrum(p2, 2.0, 1, '0')
    s3 = Spectrum(p3, 3.0, 1, '0')

    pm = PeakMap([s0,s1,s2,s3])

    integrator = dict(configs.peakIntegrators).get("trapez")
    integrator.setPeakMap(pm)
    
    assert integrator.integrate(1.4, 2.5, 0, 3)["area"] == 5.0
    assert integrator.integrate(1.4, 2.5, 0, 2)["area"] == 4.0

    assert integrator.integrate(0.4, 2.5, 0, 3)["area"] == 6.5
    assert integrator.integrate(0.4, 2.5, 0, 2)["area"] == 5.0
    
    assert integrator.integrate(0.4, 3.0, 0, 3)["area"] == 14


    # one level 2 spec:
    s1 = Spectrum(p1, 1.0, 2, '0')
    pm = PeakMap([s0,s1,s2,s3])
    integrator.setPeakMap(pm)
    
    assert integrator.integrate(1.4, 2.5, 0, 3)["area"] == 5.0
    assert integrator.integrate(1.4, 2.5, 0, 2)["area"] == 4.0

    assert integrator.integrate(0.4, 2.5, 0, 3)["area"] == 7.5
    assert integrator.integrate(0.4, 2.5, 0, 2)["area"] == 6.0
    
    assert integrator.integrate(0.4, 3.0, 0, 3)["area"] == 13.5


