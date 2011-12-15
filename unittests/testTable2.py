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
    assert t.a.len() == 3

    t.addColumn("b", None)
    assert t.b.max() == None
    assert t.b.min() == None
    assert t.b.mean() == None
    assert t.b.std() == None
    assert t.b.hasNone()
    assert t.b.len() == 3
    assert t.b.countNone() == 3

    t.addColumn("c",[None, None, 1])

    assert t.c.uniqueNotNone() == 1

    assert (t.a+t.c)() == [None, None , 4]
    assert (t.a+t.c).sum() == 4
    apc = (t.a+t.c).toTable("a_plus_c")
    assert apc.colNames == ["a_plus_c"]
    assert apc.colTypes == [int]
    assert apc.a_plus_c() == [ None, None , 4]

    assert (apc.a_plus_c - t.a)() == [None, None, 1]


def testAggregateOperation():
    t = ms.toTable("a", [ 1, 2, 2, 3, 3, 3, 3])
    t.addColumn("b", [None, None, 2, 0, 3, 4, 9])
    t._print()
    t.aggregate(t.b.sum, "sum", "a")
    t.aggregate(t.b.hasNone, "hasNone", "a")
    t.aggregate(t.b.countNone, "countNone", "a")
    t.aggregate(t.b.len, "len", "a")
    t.aggregate(t.b.std*t.b.std, "var", "a")
    t.aggregate(t.b.mean, "mean", "a")
    t._print(w=8)
    assert t.sum.values == [None, 2, 2, 16, 16, 16, 16]
    assert t.var.values == [None, 0, 0, 10.5, 10.5, 10.5, 10.5]
    assert t.mean.values == [None, 2, 2, 4, 4, 4, 4]
    assert t.hasNone.values == [1, 1, 1, 0, 0, 0, 0]
    assert t.countNone.values == [1, 1, 1, 0, 0, 0, 0]
    assert t.len.values == [1, 2, 2, 4, 4, 4, 4]

def testUniqeRows():
    t = ms.toTable("a", [1,1,2,2,3,3])
    t.addColumn("b",    [1,1,1,2,3,3])
    u = t.uniqueRows()
    assert u.a.values == [1,2,2,3]
    assert u.b.values == [1,1,2,3]
    assert len(u.colNames) == 2
    u.info()


def testAggWIthIterable():
    t = ms.toTable("a", [ (1,2), None ])
    t.aggregate(t.a.uniqueNotNone, "an")
    assert t.an.values == [ (1,2), (1,2)]
    assert t.a.values == [ (1,2), None]

def testSpecialFormats():
    for name in ["mz", "mzmin", "mzmax", "mw", "m0"]:
        t = ms.toTable(name, [ 1.0,2, None ])
        assert t.colFormatters[0](1) == "1.00000", t.colFormatters[0](1)

    for name in ["rt", "rtmin", "rtmax"]:
        t = ms.toTable(name, [ 1.0,2, None ])
        assert t.colFormatters[0](120) == "2.00m"
