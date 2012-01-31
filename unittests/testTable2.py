import ms

from libms.DataStructures.Table import Table, toOpenMSFeatureMap


def testFullJoin():
    t = ms.toTable("a", [None, 2, 3])
    t2 = t.join(t, True)
    assert len(t2) == 9
    assert t2.a.values == [ None, None, None, 2, 2, 2, 3, 3, 3]
    assert t2.a__0.values == t.a.values * 3


def testIfNotNoneElse():
    t = ms.toTable("a", [None, 2, 3])
    t.addColumn("b", t.a.ifNotNoneElse(3))
    t.addColumn("c", t.a.ifNotNoneElse(t.b+1))

    assert t.b.values == [ 3,2,3]
    assert t.c.values == [ 4,2,3]

def testPow():
    t = ms.toTable("a", [None, 2, 3])
    t.addColumn("square", t.a.pow(2))
    assert t.square.values == [None, 4, 9 ], t.square.values

def testApply():
    t = ms.toTable("a", [None, 2, 3])
    t.addColumn("id", (t.a*t.a).apply(lambda v: int(v**0.5)))
    assert t.id.values == [None, 2, 3 ]


def testApplyUfun():
    import numpy
    t = ms.toTable("a", [None, 2.0, 3])

    print numpy.log
    t.addColumn("log", t.a.apply(numpy.log))
    assert t.colTypes == [ float, float]


def testNonBoolean():
    t = ms.toTable("a", [])
    try:
        not t.a
    except:
        pass
    else:
        raise Exception()



def testForDanglingReferences():
    t = ms.toTable("a", [None, 2, 2])
    t2 = t.join(t, True)

    # test if result is a real copy, no references to original
    # tables are left
    t2.rows[0][0]=3
    assert t.rows[0][0] == None
    t2.rows[0][1]=3
    assert t.rows[0][0] == None


    t2 = t.leftJoin(t, True)
    t2.rows[0][0]=3
    assert t.rows[0][0] == None
    t2.rows[0][1]=3
    assert t.rows[0][0] == None

    t2 = t.filter(True)
    t2.rows[0][0]=3
    assert t.rows[0][0] == None


    tis = t.splitBy("a")
    tis[0].rows[0][0] = 7
    assert t.a.values == [ None, 2, 2]

    tis[1].rows[0][0] = 7
    assert t.a.values == [ None, 2, 2]

    tn = t.uniqueRows()
    tn.rows[0][0] = 7
    tn.rows[-1][0]=7
    assert t.a.values == [ None, 2, 2]

    tn = t.aggregate(t.a.max, "b") # , groupBy = "a")
    tn.rows[0][0]=7
    tn.rows[-1][0]=7
    assert t.a.values == [ None, 2, 2]

    tn = t.aggregate(t.a.max, "b", groupBy = "a")
    tn.rows[0][0]=7
    tn.rows[-1][0]=7
    assert t.a.values == [ None, 2, 2]

def testSupportedPostfixes():

    names = "mz mzmin mzmax mz0 mzmin0 mzmax0 mz1 mzmax1 mzmin__0 mzmax__0 mz__0 "\
            "mzmax3 mz4 mzmin4".split()


    t = Table(names, [float]*len(names), [None]*len(names), circumventNameCheck=True)
    assert len(t.supportedPostfixes(["mz"])) == len(names)
    assert t.supportedPostfixes(["mz", "mzmin"]) == [ "", "0", "4", "__0"]
    assert t.supportedPostfixes(["mz", "mzmin", "mzmax"]) == ["", "0", "__0"]



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

    # column from other table !
    t.addColumn("apc", apc.a_plus_c)
    assert t.apc.values==[None, None, 4], t.apc.values

    # column from other table !
    t2 = t.filter(apc.a_plus_c)
    assert len(t2) == 1
    assert  t2.apc.values == [4]


def testAggregateOperation():
    t = ms.toTable("a", [ 1, 2, 2, 3, 3, 3, 3])
    t.addColumn("b", [None, None, 2, 0, 3, 4, 9])
    t._print()
    t = t.aggregate(t.b.sum, "sum", groupBy="a")
    t = t.aggregate(t.b.hasNone, "hasNone", groupBy="a")
    t = t.aggregate(t.b.countNone, "countNone", groupBy="a")
    t = t.aggregate(t.b.count, "count", groupBy="a")
    t = t.aggregate(t.b.count - t.b.countNotNone, "countNone2", groupBy="a")
    t = t.aggregate(t.b.std*t.b.std, "var", groupBy="a")
    t = t.aggregate(t.b.mean, "mean", groupBy="a")
    t._print(w=8)
    assert t.sum.values == [None, 2, 2, 16, 16, 16, 16]
    assert t.var.values == [None, 0, 0, 10.5, 10.5, 10.5, 10.5]
    assert t.mean.values == [None, 2, 2, 4, 4, 4, 4]
    assert t.hasNone.values == [1, 1, 1, 0, 0, 0, 0]
    assert t.countNone.values == [1, 1, 1, 0, 0, 0, 0]
    assert t.countNone.values == t.countNone2.values
    assert t.count.values == [1, 2, 2, 4, 4, 4, 4]

def testUniqeRows():
    t = ms.toTable("a", [1,1,2,2,3,3])
    t.addColumn("b",    [1,1,1,2,3,3])
    u = t.uniqueRows()
    assert u.a.values == [1,2,2,3]
    assert u.b.values == [1,1,2,3]
    assert len(u.colNames) == 2
    u.info()

def testInplaceColumnmodification():
    t = ms.toTable("a", [1,2,3,4])
    t.a += 1
    assert t.a.values == [ 2,3,4,5]
    t.a *= 2
    assert t.a.values == [ 4,6,8,10]
    t.a /= 2
    assert t.a.values == [ 2,3,4,5]
    t.a -= 1
    assert t.a.values == [ 1, 2,3,4]

    t.a.modify(lambda v: 0)
    assert t.a.values == [ 0, 0, 0, 0]



def testAggWithIterable():
    t = ms.toTable("a", [ (1,2), None ])
    t = t.aggregate(t.a.uniqueNotNone, "an")
    assert t.an.values == [ (1,2), (1,2)]
    assert t.a.values == [ (1,2), None]

def testSpecialFormats():
    for name in ["mz", "mzmin", "mzmax", "mw", "m0"]:
        t = ms.toTable(name, [ 1.0,2, None ])
        assert t.colFormatters[0](1) == "1.00000", t.colFormatters[0](1)

    for name in ["rt", "rtmin", "rtmax"]:
        t = ms.toTable(name, [ 1.0,2, None ])
        assert t.colFormatters[0](120) == "2.00m"



def testToOpenMSFeatureMap():
    t = Table("mz rt".split(), [float, float], 2 * ["%.6f"])
    fm = toOpenMSFeatureMap(t)
    assert fm.size() == 0

    t.addRow([1.0, 2.0])
    fm = toOpenMSFeatureMap(t)
    assert fm.size() == 1

    f = fm[0]
    assert f.getMZ() == 1.0 # == ok, as no digits after decimal point
    assert f.getRT() == 2.0 # dito
