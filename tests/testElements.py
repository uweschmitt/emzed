from libms.Chemistry.Elements import Elements, MonoIsotopicElements
from libms.Chemistry.Tools import monoisotopicMass
def testElements():
    el = MonoIsotopicElements()
    el2 = MonoIsotopicElements()
    assert el.rows is el2.rows # check if borg is working. which reduces startup

    el.sortBy("number")
    assert el.symbol.values[0] == "H"
    assert el.name.values[0] == "Hydrogen"
    assert abs(el.m0.values[0]-1.0078250319)<1e-7

    m0H = monoisotopicMass("H")
    assert abs(m0H-el.m0.values[0])<1e-12
    m0H = monoisotopicMass("H2")
    assert abs(m0H-2*el.m0.values[0])<1e-12

    assert abs(monoisotopicMass("NaCl")-57.9586219609)<1e-9, monoisotopicMass("NaCl")


