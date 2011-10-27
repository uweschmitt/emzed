from ..DataStructures.MSTypes import PeakMap
import pyOpenMS

def alignPeakMapsWithPoseClustering(peakMaps, showProgress=True):
    try:
        exps = [ pm.toMSExperiment() for pm in peakMaps ]
    except:
        raise ValueError("need list of peakMaps as input")

    algo = pyOpenMS.MapAlignmentAlgorithmPoseClustering()
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
