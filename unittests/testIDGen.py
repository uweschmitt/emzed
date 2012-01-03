import ms
import numpy

def testIdGen():
    t = ms.distributionTable("S4C4", R=50000)
    assert len(t) == 4
    t = ms.distributionTable("S4C4", R=10000)
    assert len(t) == 3
    t._print()
    assert t.mf.values == ["S4C4"] * 3
    assert numpy.linalg.norm(numpy.array(t.abundance.values)-[1.0, 0.073, 0.181]) < 1e-3
    assert numpy.linalg.norm(numpy.array(t.mass.values)-[175.888283, 176.889972, 177.884079]) < 1e-6

