

def reintegrate(ftable, integratorid="std", showProgress = True):
    from configs import peakIntegrators
    from libms.DataStructures.Table import Table
    from libms.DataStructures.MSTypes import PeakMap
    import sys
    import numpy as np
    import time

    assert isinstance(ftable, Table)
    isftab = ftable.hasColumn("mz") and\
            ftable.hasColumn("mzmin") and\
            ftable.hasColumn("mzmax") and\
            ftable.hasColumn("rt") and\
            ftable.hasColumn("rtmin") and\
            ftable.hasColumn("rtmax") and\
            ftable.hasColumn("peakmap")

    assert isftab, "at least one column named mz, mzmin, mzmax, rt, rtmin, "\
                   "rtmax, peakmap missing"

    integrator = dict(peakIntegrators).get(integratorid)
    if integrator is None:
        raise Exception("unknown integrator '%s'" % integratorid)

    started = time.time()
    peakmaps = set(ftable.getColumn("peakmap").values)
    assert len(peakmaps) == 1, "not exactly one peakmap in table"
    peakmap = peakmaps.pop()
    assert isinstance(peakmap, PeakMap)

    integrator.setPeakMap(peakmap)

    hasSN = "sn" in ftable.colNames
    colNames = ["mz", "mzmin", "mzmax", "rt", "rtmin", "rtmax", "peakmap"]

    getIndex = ftable.getIndex

    colTypes = [ ftable.colTypes[getIndex(name)] for name in colNames ]
    colFormats = [ ftable.colFormats[getIndex(name)] for name in colNames ]

    if hasSN:
          colNames.append("sn")
          colTypes.append(ftable.colTypes[getIndex("sn")])
          colFormats.append(ftable.colFormats[getIndex("sn")])

    colNames += [ "intbegin", "intend", "method", "area", "rmse", "params",
                  "rts", "chromatogram" ]
    colTypes += [ float, float, str, float, float, object, object, object ]
    fmt = '''"%.2fm" % o'''
    colFormats += [ fmt, fmt, "%s", "%.2e", "%.2e", None, None, None ]

    rows = []
    lastcent = -1
    for i, row in enumerate(ftable):
        if showProgress:
            cent = ((i+1)*20)/len(ftable) # integer div here !
            if cent != lastcent:
                print cent*5,
                sys.stdout.flush()
                lastcent = cent
        mz = ftable.get(row, "mz")
        mzmin = ftable.get(row, "mzmin")
        mzmax = ftable.get(row, "mzmax")
        rt = ftable.get(row, "rt")
        rtmin = ftable.get(row, "rtmin")
        rtmax = ftable.get(row, "rtmax")

        intbegin = rtmin
        intend   = rtmax

        method = integratorid

        result = integrator.integrate(mzmin, mzmax, intbegin, intend)

        newrow = [mz, mzmin, mzmax, rt, rtmin, rtmax, peakmap ]
        if hasSN:
            newrow.append(ftable.get(row, "sn"))
        newrow.extend([intbegin, intend, method, result["area"], result["rmse"],
                      result["params"], result["rts"], result["chromatogram"]])

        rows.append(newrow)

    title = "" if ftable.title is None else ftable.title
    meta = ftable.meta.copy()
    meta["reintegrated"]=True
    needed = time.time() - started
    minutes = int(needed)/60
    seconds = needed - minutes * 60
    sources = ftable.sources
    print
    print
    if minutes:
        print "needed %d minutes and %.1f seconds" % (minutes, seconds)
    else:
        print "needed %.1f seconds" % seconds
    return Table(colNames, colTypes, colFormats, rows, "reintegrated: "+title,
                 meta=meta, sources=sources)
