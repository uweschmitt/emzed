def __format_array(a):
    """ declared on module scope, else Table could not be pickled """
    return "array(%r)" % a.shape

def reintegrate(ftable, integratorid="std", showProgress = True):
    from configs import PeakIntegrators
    from libms.DataStructures import FeatureTable
    import sys
    import numpy as np

    assert isinstance(ftable, FeatureTable)
    integrator = PeakIntegrators.get(integratorid)
    if integrator is None:
        raise Exception("unknown integrator '%s'" % integratorid)

    integrator.setPeakMap(ftable.ds)

    hasSN = "sn" in ftable.colNames
    colNames = ["mz", "mzmin", "mzmax", "rt", "rtmin", "rtmax"] 

    colTypes = [ ftable.colTypes[ftable.colNames.index(name)] for name in colNames ]
    colFormats = [ ftable.colFormats[ftable.colNames.index(name)] for name in colNames ]
     

    if hasSN: 
          colNames.append("sn")
          colTypes.append(ftable.colTypes[ftable.colNames.index("sn")])
          colFormats.append(ftable.colFormats[ftable.colNames.index("sn")])

    colNames += [ "intbegin", "intend", "method", "area", "rmse", "smoothed"  ]
    colTypes += [ float, float, str, float, float, np.ndarray ]
    colFormats += [ "%.2f", "%2.f", "%s", "%.1f", "%.1f", __format_array ]

    rows = []
    lastcent = -1
    for i, row in enumerate(ftable):
        if showProgress:
            cent = i*10/(len(ftable)-1)
            if cent != lastcent:
                print cent*10,
                sys.stdout.flush()
                lastcent = cent
        mz = ftable.get(i, "mz")
        mzmin = ftable.get(i, "mzmin")
        mzmax = ftable.get(i, "mzmax")
        rt = ftable.get(i, "rt")
        rtmin = ftable.get(i, "rtmin")
        rtmax = ftable.get(i, "rtmax")

        intbegin = rtmin
        intend   = rtmax
        
        method = integratorid

        result = integrator.integrate(mzmin, mzmax, intbegin, intend)
        
        row = [mz, mzmin, mzmax, rt, rtmin, rtmax ]
        if hasSN:
            row.append(ftable.get(i, "sn"))
        row.extend([intbegin, intend, method, result["area"], result["rmse"], result["smoothed"]])

        rows.append(row)

    return FeatureTable(ftable.ds, colNames, colTypes, rows, colFormats, "reintegrated "+ftable.title)
        
        
    
        
