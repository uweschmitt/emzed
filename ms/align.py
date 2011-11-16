def alignFeatureTables(tables, destination = None, nPeaks=-1, numBreakpoints=5):

    import os.path
    import pyOpenMS as P
    import copy
    from  libms.DataStructures.Table import toOpenMSFeatureMap, Table
    import custom_dialogs

    for table in tables:
        assert isinstance(table, Table), "non table object in tables"
        table.requireColumn("mz"), "need mz column for alignment"
        table.requireColumn("rt"), "need rt column for alignment"

    if destination is None:
        destination = custom_dialogs.askForDirectory()
        if destination is None:
            print "aborted"
            return

    assert os.path.isdir(os.path.abspath(destination)), "target is no directory"

    # setup algorithm
    ma = P.MapAlignmentAlgorithmPoseClustering()
    ma.setLogType(P.LogType.CMD)
    pp = ma.getDefaults()
    pp.setValue(P.String("superimposer:num_used_points"),
                P.DataValue(nPeaks),
                P.String(),
                P.StringList())
    ma.setParameters(pp)

    # convert to pyOpenMS types and find map with max num features which
    # is taken as refamp:
    fms = [ (toOpenMSFeatureMap(table), table) for table in tables]
    refmap, reftable = max(fms, key=lambda (fm, t): fm.size())
    print
    print "refmap is", os.path.basename(reftable.meta.get("source","<noname>"))
    print
    results = []
    for fm, table in fms:
        table = copy.deepcopy(table) # so we do not modify existing table !
        if fm is refmap:
            results.append(table)
            continue
        sources = set(table.getColumn("source").values)
        assert len(sources)==1, "multiple sources in table"
        source = sources.pop()
        filename = os.path.basename(source)
        print "align", filename
        fmneu, ts = __align(ma, refmap, fm, numBreakpoints)
        __plot_and_save(ts, filename, destination)
        __adaptRtValuesInTable(table, fmneu)
        results.append(table)
    for t in results:
        t.meta["aligned"] = True
    return results

def __align(ma, refmap, fm, numBreakpoints):
    # be careful: alignFeatureMaps modifies second arg,
    # so you MUST NOT put the arg as [] into this
    # function ! in this case you have no access to the calculated
    # transformations.
    import pyOpenMS as P
    ts = []
    ma.alignFeatureMaps([refmap, fm], ts)
    assert len(ts) == 2 # ts is now filled !!!!

    # fit transformations with a spline
    bps = numBreakpoints
    pp = P.Param()
    pp.setValue(P.String("num_breakpoints"), P.DataValue(bps), P.String(),
                                             P.StringList())
    ma.fitModel(P.String("b_spline"), pp, ts)
    # be careful: transformFeatureMaps modifies first arg,
    # so you MUST NOT put the args as [refmamp, fm] into this
    # function ! in this case you have no access to the transformed
    # data.
    toalign = [refmap, fm]
    ma.transformFeatureMaps(toalign, ts)
    fmneu = toalign[1]
    assert fmneu is not fm # arg is modified !
    # transformation done 
    return fmneu, ts

def __plot_and_save(ts, filename, destination):
    import numpy as np
    import pylab
    import os.path
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

def __adaptRtValuesInTable(tableOld, fmapAligned):
    # test for matching
    assert fmapAligned.size() == len(tableOld)
    irt = tableOld.getIndex("rt")
    irtmin = tableOld.getIndex("rtmin")
    irtmax = tableOld.getIndex("rtmax")
    for i in range(len(tableOld)):
        row = tableOld.rows[i]
        rtold = row[irt]
        rnew = fmapAligned[i].getRT()
        diff = rnew - rtold
        row[irt] = rnew
        row[irtmin] += diff
        row[irtmax] += diff
