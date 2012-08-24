#encoding: latin-1
import ms
import mass

def testFormGen():

    mf = "C6H12O3"
    m0 = mass.of(mf)

    t = ms.formulaTable(m0-0.001, m0+0.001, C=(0,100), H=(0, 100), O=(0, 110), N=0, P=0, S=0)
    assert len(t) == 1, len(t)
    assert t.mf.values == [mf]
    t = ms.formulaTable(m0-0.005, m0+0.005, C=(0,100), H=(0, 100), O=(0, 110))
    t.print_()
    assert len(t) == 3, len(t)
    assert mf in t.mf.values
    assert "C2H8N6O" in t.mf.values
    assert "C5H13N2P" in t.mf.values



# vim: ts=4 et sw=4 sts=4

