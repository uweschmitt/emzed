from collections import defaultdict as  _defaultdict
from scipy.stats import f_oneway as _f_oneway, kruskal as _kruskal
import numpy as _numpy

from ..DataStructures.Table import Table


def _getSamples(factorColumn, dependentColumn, minsize=1):
    factors, _, _ = factorColumn._eval(None)
    dependents, _, _ = dependentColumn._eval(None)
    groups = _defaultdict(list)
    for factor, depenent in zip(factors, dependents):
        groups[factor].append(depenent)
    samples = groups.values()
    if any(len(s) < minsize for s in samples):
        print "WARNING: sample has less than %d subjects" % minsize
    return map(_numpy.array, samples)


def oneWayAnova(factorColumn, dependentColumn):
    F, p = _f_oneway(*_getSamples(factorColumn, dependentColumn))
    return F, p


def kruskalWallis(factorColumn, dependentColumn):
    H, p = _kruskal(*_getSamples(factorColumn, dependentColumn, 5))
    return H, p


def _runStatistcsOnTables(tableSet1, tableSet2, idColumn, valueColumn,
                          pCalculator):
    ids = set()
    for t in tableSet1:
        ids.update(t.getColumn(idColumn).values)
    for t in tableSet2:
        ids.update(t.getColumn(idColumn).values)

    result = Table(["id", "n1", "n2",
                    "avg1_" + valueColumn, "std1_" + valueColumn,
                    "avg2_" + valueColumn, "std2_" + valueColumn,
                    "p_value"],
                   [str, int, int] + 5 * [float],
                   ["%s", "%d", "%d"] + 5 * ["%.2e"])

    for id_ in ids:
        samples1 = []
        for t in tableSet1:
            subt = t.filter(t.getColumn(idColumn) == id_)
            samples1.extend(subt.getColumn(valueColumn).values)
        samples2 = []
        for t in tableSet2:
            subt = t.filter(t.getColumn(idColumn) == id_)
            samples2.extend(subt.getColumn(valueColumn).values)

        samples1 = _numpy.array([s for s in samples1 if s is not None])
        samples2 = _numpy.array([s for s in samples2 if s is not None])

        p = pCalculator(samples1, samples2)

        result.addRow([id_,
                      len(samples1), len(samples2),
                      _numpy.mean(samples1), _numpy.mean(samples2),
                      _numpy.std(samples1), _numpy.std(samples2),
                      p])
    return result


def oneWayAnovaOnTables(tableSet1, tableSet2, idColumn, valueColumn):
    result = _runStatistcsOnTables(tableSet1, tableSet2, idColumn, valueColumn,
             lambda s1, s2: _f_oneway(s1, s2)[1])
    result.title = "ANOVA ANALYSIS"
    return result


def kruskalWallisOnTables(tableSet1, tableSet2, idColumn, valueColumn):
    result = _runStatistcsOnTables(tableSet1, tableSet2, idColumn, valueColumn,
             lambda s1, s2: _kruskal(s1, s2)[1])
    result.title = "KRUSKAL WALLIS ANALYSIS"
    return result
