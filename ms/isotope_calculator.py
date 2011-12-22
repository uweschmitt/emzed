
def _setupIsotopeDistributionGenerator(formula, R, fullC13, minp, **kw):
    from libms.Chemistry.IsotopeDistribution import IsotopeDistributionGenerator
    if fullC13:
        kw.update(dict(C13=1.0))
    return IsotopeDistributionGenerator(formula, R, minp, **kw)


def plotDistribution(formula, R=None, fullC13=False, minp=0.01, **kw):
    gen = _setupIsotopeDistributionGenerator(formula, R, fullC13, minp, **kw)
    gen.show()

def distributionTable(formula, R=None, fullC13=False, minp=0.01, **kw):
    from libms.DataStructures.Table import Table
    gen = _setupIsotopeDistributionGenerator(formula, R, fullC13, minp, **kw)
    t = Table(["mf", "mass", "abundance"], [str, float, float],
                                           ["%s", "%.6f", "%.3f"], [])
    for mass, abundance in gen.getCentroids():
        t.addRow([formula, mass, abundance], False)
    t.resetInternals()
    return t


