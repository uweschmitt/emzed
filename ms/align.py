def alignFeatureTables(tables, destination = None, nPeaks=-1, numBreakpoints=5):

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


    ma = P.MapAlignmentAlgorithmPoseClustering()
    ma.setLogType(P.LogType.CMD)
    pp = ma.getDefaults()
    pp.setValue(P.String("superimposer:num_used_points"),
                P.DataValue(nPeaks),
                P.String(),
                P.StringList())
    ma.setParameters(pp)

    fms = [table.toOpenMSFeatureMap() for table in tables]
    refmap = max(fms, key=lambda fm: fm.size())
    results = []
    for fm, table in zip(fms, tables):
        table = copy.deepcopy(table)
        filename = os.path.basename(table.ds.meta["source"])
        if fm is refmap:
            results.append(table)
            continue

        print "align", filename
        ts = []
        ma.alignFeatureMaps([refmap, fm], ts)
        bps = numBreakpoints
        pp = P.Param()
        pp.setValue(P.String("num_breakpoints"), P.DataValue(bps), P.String(),
                                                 P.StringList())
        ma.fitModel(P.String("b_spline"), pp, ts)
        ma.transformFeatureMaps([refmap, fm], ts)
        dtp = ts[1].getDataPoints()
        x,y = zip(*dtp)
        x = np.array(x)
        y = np.array(y)
        pylab.clf()
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

