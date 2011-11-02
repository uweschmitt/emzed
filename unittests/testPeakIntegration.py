
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


def testPeakIntegration():
    
    integrator = dict(configs.peakIntegrators).get("asym_gauss")
    _, _, params = run(integrator, 30584.3, 7251.2)

    assert abs(params[0]- 36775.0) < 1.0, params[0]
    assert abs(params[1]- 0.2007) < 0.001, params[1]
    assert abs(params[2]- 0.1921) < 0.001, params[2]
    assert abs(params[3]- 325.7) < 0.1, params[3]

    integrator = dict(configs.peakIntegrators).get("emg")

    run(integrator,  1.545513e5, 7.43277e3)

    integrator = dict(configs.peakIntegrators).get("trapez")

    run(integrator,  120481.9, 0.0)

    integrator = dict(configs.peakIntegrators).get("std")
    run(integrator,  119149.7, 6854.8)


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


