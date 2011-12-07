

def integrate(ftable, integratorid="std", showProgress = True):
    """ integrates features  in ftable.
        returns processed table. *ftable* is not changed inplace
    """
    from configs import peakIntegrators
    from libms.DataStructures.Table import Table
    from libms.DataStructures.MSTypes import PeakMap
    import sys
    import numpy as np
    import time

    assert isinstance(ftable, Table)

    neededColumns = ["mz", "mzmin", "mzmax", "rt", "rtmin", "rtmax", "peakmap"]
    foundColumns = [ftable.hasColumn(n) for n in neededColumns]
    if not all(foundColumns):
        missing = [n for n in neededColumns if not ftable.hasColumn(n)]
        raise Exception("is no ftab. cols missing: "+", ".join(missing))

    started = time.time()
    integrator = dict(peakIntegrators).get(integratorid)
    if integrator is None:
        raise Exception("unknown integrator '%s'" % integratorid)

    peakmaps = set(ftable.getColumn("peakmap").values)
    assert len(peakmaps) == 1, "not exactly one peakmap in table"
    peakmap = peakmaps.pop()
    assert isinstance(peakmap, PeakMap)

    integrator.setPeakMap(peakmap)

    resultTable = ftable.buildEmptyClone()

    newCols = [ "intbegin", "intend", "method", "area", "rmse", "params",]
    # drop columns which are integration related
    for col in newCols:
        if resultTable.hasColumn(col):
            resultTable.dropColumn(col)

    resultTable.colNames += newCols
    resultTable.colTypes += [ float, float, str, float, float, object, ]
    fmt = '''"%.2fm" % (o/60.0)'''
    resultTable.colFormats += [ fmt, fmt, "%s", "%.2e", "%.2e", None, ]

    lastcent = -1
    for i, row in enumerate(ftable):
        if showProgress:
            cent = ((i+1)*20)/len(ftable) # integer div here !
            if cent != lastcent:
                print cent*5,
                sys.stdout.flush()
                lastcent = cent
        intbegin = ftable.get(row, "rtmin")
        intend = ftable.get(row, "rtmax")
        mzmin = ftable.get(row, "mzmin")
        mzmax = ftable.get(row, "mzmax")
        result = integrator.integrate(mzmin, mzmax, intbegin, intend)
        # take existing values which are not integration realated:
        newrow = [ ftable.get(row, n) for n in resultTable.colNames\
                                      if n not in newCols]
        newrow.extend([intbegin, intend, integratorid, result["area"],
                       result["rmse"], result["params"], ])

        resultTable.addRow(newrow)

    resultTable.meta["integrated"]=True
    resultTable.title = "integrated: "+resultTable.title
    needed = time.time() - started
    minutes = int(needed)/60
    seconds = needed - minutes * 60
    print
    if minutes:
        print "needed %d minutes and %.1f seconds" % (minutes, seconds)
    else:
        print "needed %.1f seconds" % seconds
    resultTable.resetInternals()
    return resultTable
