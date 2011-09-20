
import configs, ms

def run(integrator, areatobe, rmsetobe):
    assert len(str(integrator))>0

    try:
        ds = run.ds 
    except:
        ds = run.ds =  ms.loadMap("data/SHORT_MS2_FILE.mzData")

    integrator.setPeakMap(ds)

    rtmin = ds.specs[0].RT
    rtmax = ds.specs[30].RT

    mzmin = ds.specs[0].peaks[10,0]
    mzmax = ds.specs[0].peaks[-10,0]

    result = integrator.integrate(mzmin, mzmax, rtmin, rtmax)
        
    area=result.get("area")
    rmse=result.get("rmse")

    print "area: is=%e  tobe=%e" % (area, areatobe)
    print "rmse: is=%e  tobe=%e" % (rmse, rmsetobe)

    assert abs(area-areatobe) < .1,  area
    assert abs(rmse-rmsetobe) < .1,  rmse

    #assert abs(area-121858.8) < .1,  area
    #assert abs(rmse-6904.9) < .1,  rmse

def testPeakIntegration():
    integrator = dict(configs.peakIntegrators).get("trapez")

    run(integrator,  122645.12, 0.0)

    integrator = dict(configs.peakIntegrators).get("std")
    run(integrator, 121858.8, 6904.9)

    
    integrator = dict(configs.peakIntegrators).get("asym_gauss")
    run(integrator, 29008.7, 7156.6)

    #integrator.setPeakMap(ds)

    #result = integrator.integrate(mzmin, mzmax, rtmin, rtmax)
        
    #area=result.get("area")
    #rmse=result.get("rmse")

    #assert abs(area-29008.7) < .1,  area
    #assert abs(rmse-7156.6) < .1,  rmse
