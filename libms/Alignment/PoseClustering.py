from ..DataStructures.MSTypes import PeakMap
import pyOpenMS
import numpy as np
import os

def alignPeakMapsWithPoseClustering(peakMaps, refIdx=None,showProgress=False, 
                                    max_num_peaks_considered=None,
                                    plotAlignment=False, doShow=True):
    try:
        exps = [ pm.toMSExperiment() for pm in peakMaps ]
    except:
        raise ValueError("need list of peakMaps as input")

    algo = pyOpenMS.MapAlignmentAlgorithmPoseClustering()
    if max_num_peaks_considered is not None:
        pp = algo.getDefaults()
        pp.setValue(pyOpenMS.String("max_num_peaks_considered"), 
                    pyOpenMS.DataValue(max_num_peaks_considered), 
                    pyOpenMS.String(),
                    pyOpenMS.StringList())
        algo.setParameters(pp)
    if showProgress:
        algo.setLogType(pyOpenMS.LogType.CMD)
    transformations = []

    if refIdx is not None:
        # open ms refidx is 1-based !
        algo.setReference(refIdx+1, pyOpenMS.String()) 
    algo.alignPeakMaps(exps, transformations)
    s = pyOpenMS.String()
    p = pyOpenMS.Param()
    algo.getDefaultModel(s, p)
    key = pyOpenMS.String("symmetric_regression")
    value = pyOpenMS.DataValue("false")
    p.setValue(key, value, pyOpenMS.String(), pyOpenMS.StringList())
    algo.fitModel(s, p, transformations)

    if plotAlignment:
        import pylab as pl
        nsub = len(peakMaps)-1 if len(peakMaps)-1 < 4  else 4
        i = 0
        for pm, trans in zip(peakMaps, transformations):
            datapoints = trans.getDataPoints()
            if datapoints: # one is empty
                if i%nsub==0:
                    pl.figure()
                pl.subplot(nsub,1, 1 + i % nsub)
                title = os.path.basename(pm.meta.get("source", ""))
                pl.title(title)
                # unzip (x,y) tuples and convert to array:
                x, y = map(np.array, zip(*datapoints))
                # fit values
                yfitted = np.array([trans.apply(xi) for xi in x])
                # plot fitted model vs data points
                pl.plot(x, y-x, label="in data")
                pl.plot(x, yfitted-x, label="fitted")
                pl.xlabel("RT")
                pl.ylabel("$\Delta$ RT")
                pl.legend()
                i += 1

        if doShow:
            pl.show()

    algo.transformPeakMaps(exps, transformations)
    return [ PeakMap.fromMSExperiment(e) for e in exps ] 
