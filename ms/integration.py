
def reintegrate(ftable, integratorid="std", showProgress = True):
    from configs import peakIntegrators
    from libms.DataStructures import FeatureTable
    import sys
    import numpy as np

    assert isinstance(ftable, FeatureTable)
    integrator = dict(peakIntegrators).get(integratorid)
    if integrator is None:
        raise Exception("unknown integrator '%s'" % integratorid)

    integrator.setPeakMap(ftable.ds)

    hasSN = "sn" in ftable.colNames
    colNames = ["mz", "mzmin", "mzmax", "rt", "rtmin", "rtmax"] 

    getIndex = ftable.getIndex

    colTypes = [ ftable.colTypes[getIndex(name)] for name in colNames ]
    colFormats = [ ftable.colFormats[getIndex(name)] for name in colNames ]
     

    if hasSN: 
          colNames.append("sn")
          colTypes.append(ftable.colTypes[getIndex("sn")])
          colFormats.append(ftable.colFormats[getIndex("sn")])

    colNames += [ "intbegin", "intend", "method", "area", "rmse", "intrts", "smoothed"  ]
    colTypes += [ float, float, str, float, float, np.ndarray, np.ndarray ]
    colFormats += [ "%8.2f", "%8.2f", "%s", "%.2e", "%.2e", None , None ]

    rows = []
    lastcent = -1
    for i, row in enumerate(ftable):
        if showProgress:
            cent = (i*20)/(len(ftable)-1) # integer div here !
            if cent != lastcent:
                print cent*5,
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
        row.extend([intbegin, intend, method, result["area"], result["rmse"], result["intrts"], result["smoothed"]])

        rows.append(row)

    title = "" if ftable.title is None else ftable.title
    meta = ftable.meta.copy()
    meta["reintegrated"]=True
    return FeatureTable(ftable.ds, colNames, colTypes, rows, colFormats, "reintegrated: "+title, meta=meta)
        
        
    
        
