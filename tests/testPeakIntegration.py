
import configs, ms
import numpy as np
from   libms.DataStructures import Spectrum, PeakMap
from   libms.PeakIntegration import *

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

    result = integrator.integrate(mzmin, mzmax, rtmin, rtmax, 1)
    area=result.get("area")
    rmse=result.get("rmse")

    print "area: is=%e  tobe=%e" % (area, areatobe)
    print "rmse: is=%e  tobe=%e" % (rmse, rmsetobe)


    if area > 0:
        assert abs(area-areatobe)/areatobe < .01,  area
    else:
        assert area == 0.0, area
    if rmse > 0:
        assert abs(rmse-rmsetobe)/rmsetobe < .01,  rmse
    else:
        assert rmse == 0.0, rmse

    params = result.get("params")

    rts = [ spec.rt for spec in ds.spectra ]

    x, y = integrator.getSmoothed(rts, params)

    return x,y, params

def testNoIntegration():

    integrator = dict(configs.peakIntegrators)["no_integration"]
    integrator.setPeakMap(PeakMap([]))
    result = integrator.integrate(0.0, 100.0, 0, 300, 1)
    assert result.get("area") == None
    assert result.get("rmse") == None
    assert result.get("params") == None

    rts = range(0, 600)
    x,y = integrator.getSmoothed(rts, result.get("params"))
    assert x==[]
    assert y==[]


def testPeakIntegration():

    integrator = dict(configs.peakIntegrators)["asym_gauss"]
    _, _, params = run(integrator, 1.19e5, 7.2891e3)

    #assert abs(params[0]- 12182.07) < 1.0, params
    #assert abs(params[1]- 136.9405) < 0.01, params
    #assert abs(params[2]- 8.338e-12) < 1e-14, params
    #assert abs(params[3]- 326.49) < 0.1, params

    integrator = dict(configs.peakIntegrators)["emg_exact"]

    run(integrator,  154542.79, 7.43274e3)

    integrator = dict(configs.peakIntegrators)["trapez"]

    run(integrator,  120481.9, 0.0)

    integrator = dict(configs.peakIntegrators)["std"]
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

    integrator = dict(configs.peakIntegrators)["trapez"]
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

    assert integrator.integrate(1.4, 2.5, 0, 3, msLevel=1)["area"] == 5.0
    assert integrator.integrate(1.4, 2.5, 0, 2, msLevel=1)["area"] == 4.0

    assert integrator.integrate(0.4, 2.5, 0, 3, msLevel=1)["area"] == 7.5
    assert integrator.integrate(0.4, 2.5, 0, 2, msLevel=1)["area"] == 6.0

    assert integrator.integrate(0.4, 3.0, 0, 3, msLevel=1)["area"] == 13.5

    # multiple levels shall rise exception:
    ex(lambda: integrator.integrate(0.4, 3.0, 0, 3))


def ex(f):
    e0 = None
    try:
        f()
    except Exception, e:
        e0 = e
    assert e0 is not None

def testSg():
    allrts = np.arange(10, 100)
    rts    = np.arange(1, 10)
    chromo = np.sin(allrts)
    chromo[10:]= 0

    ex(lambda: SGIntegrator(order=1, window_size=4).smooth(allrts, rts, chromo))
    ex(lambda: SGIntegrator(order=1, window_size=-1).smooth(allrts, rts, chromo))
    ex(lambda: SGIntegrator(order=4, window_size=5).smooth(allrts, rts, chromo))
