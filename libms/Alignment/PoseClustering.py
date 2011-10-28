from ..DataStructures.MSTypes import PeakMap
import pyOpenMS

def alignPeakMapsWithPoseClustering(peakMaps, showProgress=True, npeaks=None):
    try:
        exps = [ pm.toMSExperiment() for pm in peakMaps ]
    except:
        raise ValueError("need list of peakMaps as input")

    algo = pyOpenMS.MapAlignmentAlgorithmPoseClustering()
    if npeaks is not None:
        print "set npeaks=", npeaks
        pp = algo.getDefaults()
        pp.setValue(pyOpenMS.String("max_num_peaks_considered"), 
                    pyOpenMS.DataValue(npeaks), 
                    pyOpenMS.String(),
                    pyOpenMS.StringList())
        algo.setParameters(pp)
    if showProgress:
        algo.setLogType(pyOpenMS.LogType.CMD)
    transformations = []
    algo.alignPeakMaps(exps, transformations)
    s = pyOpenMS.String()
    p = pyOpenMS.Param()
    algo.getDefaultModel(s, p)
    algo.fitModel(s, p, transformations)
    algo.transformPeakMaps(exps, transformations)
    return [ PeakMap.fromMSExperiment(e) for e in exps ] 
