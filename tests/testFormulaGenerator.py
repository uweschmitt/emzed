#encoding: latin-1
import ms
import mass

def testFormGen():

    mf = "C6H12O3"
    m0 = mass.of(mf)

    t = ms.formulaTable(m0-0.001, m0+0.001, C=(0,100), H=(0, 100), O=(0, 110))
    assert len(t) == 1, len(t)
    assert t.mf.values == [mf]
    t = ms.formulaTable(m0-0.1, m0+0.1, C=(0,100), H=(0, 100), O=(0, 110))
    assert len(t) == 9, len(t)
    assert mf in t.mf.values



# vim: ts=4 et sw=4 sts=4

