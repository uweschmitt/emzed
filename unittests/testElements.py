from libms.Chemistry import Elements
def testElements():
    el = Elements()
    el2 = Elements()
    assert el.rows is el2.rows # check if borg is working. which reduces startup

    el.sortBy("number")
    assert el.symbol.values[0] == "H"
    assert el.name.values[0] == "Hydrogen"
    assert abs(el.m0.values[0]-1.0078250319)<1e-7



