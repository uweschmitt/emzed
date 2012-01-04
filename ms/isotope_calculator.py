
def _setupIsotopeDistributionGenerator(formula, R, fullC13, minp, **kw):
    from libms.Chemistry.IsotopeDistribution import IsotopeDistributionGenerator
    if fullC13:
        kw.update(dict(C=dict(C12=0.0, C13=1.0)))
    return IsotopeDistributionGenerator(formula, R, minp, **kw)


def plotIsotopeDistribution(formula, R=None, fullC13=False, minp=0.01, **kw):
    """
    plots isotopedistribution for molecule with given mass formula *formula*.

    for parameters: see isotopeDistributionTable()
    """
    gen = _setupIsotopeDistributionGenerator(formula, R, fullC13, minp, **kw)
    gen.show()

def isotopeDistributionTable(formula, R=None, fullC13=False, minp=0.01, **kw):
    """
    generates Table for most common isotopes of molecule with given mass *formula*

    If the resolution *R* is given, the measurment device is simulated, and
    overlapping peaks may merge.

    *fullC13=True* assumes that only C13 carbon is present in formula.

    Further you can give a threshhold *minp* for considering only isotope
    peaks with an abundance above the value. Standard is *minp=0.01*.

    If you have special elementary isotope abundances which differ from
    the natural abundances, you can tell that like::

        ms.isotopeDistributionTable("S4C4", C=dict(C13=0.5, C12=0.5))

    \
    """
    from libms.DataStructures.Table import Table
    gen = _setupIsotopeDistributionGenerator(formula, R, fullC13, minp, **kw)
    t = Table(["mf", "mass", "abundance"], [str, float, float],
                                           ["%s", "%.6f", "%.3f"], [])
    for mass, abundance in gen.getCentroids():
        t.addRow([formula, mass, abundance], False)
    t.resetInternals()
    return t


