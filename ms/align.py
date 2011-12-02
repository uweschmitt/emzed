def alignFeatureTables(tables, destination = None, nPeaks=-1, numBreakpoints=5,
                       forceAlign=False):

    import os.path
    import pyOpenMS as P
    import copy
    from  libms.DataStructures.Table import toOpenMSFeatureMap, Table
    import custom_dialogs

    for table in tables:
        # collect all maps
        maps = set(table.get(row, "peakmap") for row in table)
        assert len(maps) == 1, "can only align features from one single peakmap"
        map = maps.pop()
        if forceAlign:
            map.meta["aligned"]=False
        else:
            if map.meta.get("aligned"):
                message = "there are already aligned peakmaps in the "\
                          "tables.\nyou have to provide the forceAlign "\
                          "parameter of this function\nto align all tables"
                raise Exception(message)
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
        sources = set(table.source.values)
        assert len(sources)==1, "multiple sources in table"
        source = sources.pop()
        filename = os.path.basename(source)
        print "align", filename
        transformation = _computeTransformation(ma, refmap, fm, numBreakpoints)
        _plot_and_save(transformation, filename, destination)
        _adaptTable(table, transformation)
        results.append(table)
    for t in results:
        t.meta["aligned"] = True
    return results

def _computeTransformation(ma, refmap, fm, numBreakpoints):
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
    return ts[1]

def _plot_and_save(transformation, filename, destination):
    import numpy as np
    import pylab
    import os.path
    dtp = transformation.getDataPoints()
    x,y = zip(*dtp)
    x = np.array(x)
    y = np.array(y)
    pylab.clf()
    pylab.plot(x, y-x, ".")
    x.sort()
    yn = [ transformation.apply(xi) for xi in x]
    pylab.plot(x, yn-x)
    filename = os.path.splitext(filename)[0]+"_aligned.png"
    target_path = os.path.join(destination, filename)
    print "save", filename
    pylab.savefig(target_path)

def _adaptTable(table, transformation):
    import copy
    for row in table:
        rtmin = table.get(row, "rtmin")
        rtmax = table.get(row, "rtmax")
        rt    = table.get(row, "rt")
        table.set(row, "rtmin", transformation.apply(rtmin))
        table.set(row, "rtmax", transformation.apply(rtmax))
        table.set(row, "rt", transformation.apply(rt))
        if "intbegin" in table.colNames:
            intbegin = table.get(row, "intbegin")
            intend = table.get(row, "intend")
            table.set(row, "intbegin", transformation.apply(intbegin))
            table.set(row, "intend", transformation.apply(intend))

    # we know that there is only one peakmap in the table 
    peakmap = table.get(table.rows[0], "peakmap")
    peakmapNew = copy.deepcopy(peakmap)
    peakmapNew.meta["aligned"] = True
    for spec in peakmapNew:
        spec.rt = transformation.apply(spec.rt)
    for row in table:
        table.set(row, "peakmap", peakmapNew)
