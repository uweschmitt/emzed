from collections import defaultdict
from scipy.stats import f_oneway

def oneWayAnova(table, factorName, dependentName):
    factors = table.getColumn(factorName).values
    dependents = table.getColumn(dependentName).values
    groups = defaultdict(list)
    for factor, depenent in zip(factors, dependents):
        groups[factor].append(depenent)
    F, p = f_oneway(*groups.values())
    return F, p



