import ms
def testNumericSTuff():
    t = ms.toTable("a", [None, 2, 3])
    t._print()
    t.replaceColumn("a", t.a + 1.0)
    t._print()
    t.info()


def testSomeExpressions():
    t = ms.toTable("mf", ["Ag", "P", "Pb", "P3Pb", "PbP"])
    tn = t.filter(t.mf.containsElement("P"))
    assert len(tn) == 3
    tn = t.filter(t.mf.containsElement("Pb"))
    assert len(tn) == 3


def testColumnAggFunctions():
    t = ms.toTable("a", [None, 2, 3])
    assert t.a.max() == 3
    assert t.a.min() == 2
    assert t.a.mean() == 2.5
    assert t.a.std() == 0.5
    assert t.a.hasNone()
    assert t.a.len() == 3
    assert t.a.countNone() == 1

    t.addColumn("b", None)
    assert t.b.max() == None
    assert t.b.min() == None
    assert t.b.mean() == None
    assert t.b.std() == None
    assert t.b.hasNone()
    assert t.b.len() == 3
    assert t.b.countNone() == 3


def testAggregateOperation():
    t = ms.toTable("a", [ 1, 2, 2, 3, 3, 3, 3])
    t.addColumn("b", [None, None, 2, 0, 3, 4, 9])
    t._print()
    t = t.aggregate(t.b.sum(), "sum", "a")
    t = t.aggregate(t.b.hasNone(), "hasNone", "a")
    t = t.aggregate(t.b.countNone(), "countNone", "a")
    t = t.aggregate(t.b.len(), "len", "a")
    t = t.aggregate(t.b.std()*t.b.std(), "var", "a")
    t = t.aggregate(t.b.mean(), "mean", "a")
    t._print(w=8)
    assert t.sum.values == [None, 2, 2, 16, 16, 16, 16]
    assert t.var.values == [None, 0, 0, 10.5, 10.5, 10.5, 10.5]
    assert t.mean.values == [None, 2, 2, 4, 4, 4, 4]
    assert t.hasNone.values == [1, 1, 1, 0, 0, 0, 0]
    assert t.countNone.values == [1, 1, 1, 0, 0, 0, 0]
    assert t.len.values == [1, 2, 2, 4, 4, 4, 4]
