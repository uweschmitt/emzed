from libms.Statistics.Anova import oneWayAnova
import ms

def testOneWay():
    t = ms.toTable("factor", [1,2,1,2,1,1,2])
    t.addColumn("dependent", t.factor*1.1)
    F, p = oneWayAnova(t, "factor", "dependent")
    assert p<1e-7, p
    t.addColumn("dependent2", [1.01,2.01,1.02,2.02,.99, 0.98,1.98])
    F, p = oneWayAnova(t, "factor", "dependent2")
    assert abs(p-1.3e-8)/1.3e-8 < 0.01
