import elements
import mass
import abundance

def testAccessAndConsistency():
    c12 = elements.C12
    assert c12["abundance"] == abundance.C12
    assert c12["abundance"] is not None
    assert abs(c12["abundance"]-0.989) < 0.001
    assert c12["mass"] ==  mass.C12
    assert c12["name"] == "Carbon"
    assert c12["number"] == 6
    assert  mass.of("[13]C") - mass.of("C") == mass.C13-mass.C12




