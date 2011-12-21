def alignFeatureTables(tables, refTable = None, destination = None,
                       nPeaks=-1, numBreakpoints=5, maxRtDifference = 100,
                       maxMzDifference = 0.3,
                       forceAlign=False):

    """ aligns feature tables in respect to retetion times.
        the algorithme produces new tables with aligend data.
        **input tables including the assiciatoted peakmap(s) are not modified**.

        Parameters:

            - *nPeaks*: max number of peaks matched by superimposer, -1
              means: all peaks

            - *maxRtDifference*: max allowed difference in rt values for
              searching matching features.

            - *maxMzDifference*: max allowed difference in mz values for
              searching matching features.

            - *numBreakpoints*: number of break points of fitted spline.
              default:5, more points result in splines with higher variation.

            - *forceAlign*: has to be *True* to align already rt aligned tables.

            - *refTable*: extra reference table, if *None* the table
              with most features among *tables* is taken.
    """

    import os.path
    import pyOpenMS as P
    import copy
    from  libms.DataStructures.Table import toOpenMSFeatureMap, Table
    import custom_dialogs

    for table in tables:
        # collect all maps
        maps = set(table.peakmap.values)
        assert len(maps) == 1, "can only align features from one single peakmap"
        map = maps.pop()
        assert map != None, "None value for peakmaps not allowed"
        if forceAlign:
            map.meta["rt_aligned"]=False
        else:
            if map.meta.get("rt_aligned"):
                message = "there are already rt_aligned peakmaps in the "\
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

    if refTable is not None:
        maps = set(refTable.peakmap.values)
        assert len(maps) == 1, "can only align features from one single peakmap"
        map = maps.pop()
        assert map != None, "None value for peakmaps not allowed"
        refTable.requireColumn("mz"), "need mz column in reftable"
        refTable.requireColumn("rt"), "need rt column in reftable"

    assert os.path.isdir(os.path.abspath(destination)), "target is no directory"

    # setup algorithm
    ma = P.MapAlignmentAlgorithmPoseClustering()
    ma.setLogType(P.LogType.CMD)
    pp = ma.getDefaults()
    pp.setValue(P.String("superimposer:num_used_points"),
                P.DataValue(nPeaks),
                P.String(),
                P.StringList())
    pp.setValue(P.String("pairfinder:distance_RT:max_difference"),
                P.DataValue(float(maxRtDifference)),
                P.String(),
                P.StringList())
    pp.setValue(P.String("pairfinder:distance_MZ:max_difference"),
                P.DataValue(float(maxMzDifference)), # in dalton resp u. 
                P.String(),
                P.StringList())
    pp.setValue(P.String("pairfinder:distance_MZ:unit"),
                P.DataValue("Da"), # masssunits->dalton
                P.String(),
                P.StringList())
    ma.setParameters(pp)

    # convert to pyOpenMS types and find map with max num features which
    # is taken as refamp:
    fms = [ (toOpenMSFeatureMap(table), table) for table in tables]
    if refTable is None:
        refMap, refTable = max(fms, key=lambda (fm, t): fm.size())
        print
        print "REFMAP IS",
        print os.path.basename(refTable.meta.get("source","<noname>"))
        print
    else:
        refMap = toOpenMSFeatureMap(refTable)
    results = []
    for fm, table in fms:
        table = copy.deepcopy(table) # so we do not modify existing table !
        if fm is refMap:
            results.append(table)
            continue
        sources = set(table.source.values)
        assert len(sources)==1, "multiple sources in table"
        source = sources.pop()
        filename = os.path.basename(source)
        print
        print "ALIGN FEATURES FROM ", filename
        print
        transformation = _computeTransformation(ma, refMap, fm, numBreakpoints)
        _plot_and_save(transformation, filename, destination)
        _transformTable(table, transformation)
        results.append(table)
    for t in results:
        t.meta["rt_aligned"] = True
    return results

def _computeTransformation(ma, refMap, fm, numBreakpoints):
    # be careful: alignFeatureMaps modifies second arg,
    # so you MUST NOT put the arg as [] into this
    # function ! in this case you have no access to the calculated
    # transformations.
    import pyOpenMS as P
    ts = []
    ma.alignFeatureMaps([refMap, fm], ts)
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
    if len(dtp) == 0:
        raise Exception("no matches found.")

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
    print
    print "SAVE", filename
    print
    pylab.savefig(target_path)

def _transformTable(table, transformation):
    for row in table.rows:
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
    peakmap = table.peakmap.values[0]
    peakmap.meta["rt_aligned"] = True
    table.meta["rt_aligned"] = True
    for spec in peakmap.spectra:
        spec.rt = transformation.apply(spec.rt)
    table.replaceColumn("peakmap", peakmap)
