def alignFeatureTables(tables, destination = None, numBreakpoints=5):

    import os.path 
    import pylab
    import numpy as np
    import pyOpenMS as P
    import copy

    import custom_dialogs
    if destination is None:
        destination = custom_dialogs.askForDirectory()
        if destination is None:
            print "aborted"
            return

    assert os.path.isdir(os.path.abspath(destination)), "target is no directory"

    fms = [(i, table.toOpenMSFeatureMap()) for i, table in enumerate(tables)]
    # sort descending in num features
    fms.sort(key=lambda (i, fm): -fm.size())

    ma = P.MapAlignmentAlgorithmPoseClustering()
    ma.setLogType(P.LogType.CMD)

    imax, refmap = fms[0]
    results = [copy.copy(tables[imax])]
    for i, fm in fms[1:]:
        table = copy.deepcopy(tables[i])
        filename = os.path.basename(table.ds.meta["source"])
        print "align", filename
        ts = []
        ma.alignFeatureMaps([refmap, fm], ts)
        bps = numBreakpoints
        pp = P.Param()
        pp.setValue(P.String("num_breakpoints"), P.DataValue(bps), P.String(),
                                                 P.StringList())
        ma.fitModel(P.String("b_spline"), pp, ts)
        dtp = ts[1].getDataPoints()
        x,y = zip(*dtp)
        x = np.array(x)
        y = np.array(y)
        pylab.plot(x, y-x, ".")
        x.sort()
        yn = [ ts[1].apply(xi) for xi in x]
        pylab.plot(x, yn-x)
        filename = os.path.splitext(filename)[0]+"_aligned.png"
        target_path = os.path.join(destination, filename)
        print "save", filename
        pylab.savefig(target_path)
        table.alignAccordingTo(fm)
        results.append(table)
    for t in results:
        t.meta["aligned"] = True
    return results

