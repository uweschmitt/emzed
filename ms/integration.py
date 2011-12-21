

def integrate(ftable, integratorid="std", showProgress = True):
    """ integrates features  in ftable.
        returns processed table. *ftable* is not changed inplace
    """
    from configs import peakIntegrators
    from libms.DataStructures.Table import Table
    import sys
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


    resultTable = ftable.buildEmptyClone()

    newCols = [ "method", "area", "rmse", "params",]
    # drop columns which are integration related
    for col in newCols:
        if resultTable.hasColumn(col):
            resultTable.dropColumn(col)

    resultTable.colNames += newCols
    resultTable.colTypes += [ str, float, float, object, ]
    resultTable.colFormats += [ "%s", "%.2e", "%.2e", None, ]

    lastcent = -1
    for i, row in enumerate(ftable.rows):
        if showProgress:
            cent = ((i+1)*20)/len(ftable) # integer div here !
            if cent != lastcent:
                print cent*5,
                sys.stdout.flush()
                lastcent = cent
        rtmin = ftable.get(row, "rtmin")
        rtmax = ftable.get(row, "rtmax")
        mzmin = ftable.get(row, "mzmin")
        mzmax = ftable.get(row, "mzmax")
        peakmap = ftable.get(row, "peakmap")
        newrow = [ftable.get(row, n) for n in resultTable.colNames\
                                      if n not in newCols]
        if rtmin is None or rtmax is None or mzmin is None or mzmax is None\
                 or peakmap is None:
            newrow.extend([None] * len(newCols))
        else:
            integrator.setPeakMap(peakmap)
            result = integrator.integrate(mzmin, mzmax, rtmin, rtmax)
            # take existing values which are not integration realated:
            newrow.extend([integratorid, result["area"], result["rmse"],\
                           result["params"], ])

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
