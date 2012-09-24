import ms, mass

from libms.DataStructures.Table import Table, toOpenMSFeatureMap

def testBinary():
    t = ms.toTable("compound", ["Na", "NaCl", "H2O"])
    t2 = t.filter(t.compound.containsElement("Na") | t.compound.containsElement("Cl"))
    assert len(t2) == 2

def testJoinNameGeneration():

    t = ms.toTable("a",[])
    t2 = t.copy()
    t = t.join(t2, False)
    assert t.colNames== ["a", "a__0"]
    t = t.join(t2, False)
    assert t.colNames== ["a", "a__0", "a__1"]
    t = t.join(t.copy(), False)
    assert t.colNames== ["a", "a__0", "a__1", "a__2", "a__3", "a__4"]
    t.dropColumns("a")
    t = t.join(t.copy(), False)
    assert t.colNames== ["a__%d" % i for i in range(10)]

def testEmptyApply():
    t = ms.toTable("a", [])
    t.addColumn("b", t.a.apply(len))
    assert len(t) == 0
    assert t.colTypes == [object, object]

def testRound():
    # failed in ealrier versions, as np.vectorize does not like round !
    t = ms.toTable("a", [1.23, 0.5])
    t.addColumn("b", t.a.apply(round))
    assert len(t)==2
    assert t.b.values == [ 1.0, 1.0]


def testFullJoin():
    t = ms.toTable("a", [None, 2, 3])
    t2 = t.join(t, True)
    t2.print_()
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


    sub = ms.toTable("mf", ["Na", "H2O", None])

    # apply with Nones in cols
    expr = sub.mf.apply(mass.of)
    sub.addColumn("m0", expr)

    sub.addColumn("m0s", sub.m0.apply(str))
    sub.print_()
    assert sub.colTypes == [ str, float, str], sub.colTypes

    # apply without None values:
    sub = sub.filter(sub.m0 != None)
    assert len(sub) == 2
    sub.addColumn("m02", sub.mf.apply(mass.of))
    sub.addColumn("m0s2", sub.m0.apply(str))
    assert sub.colTypes == [ str, float, str, float, str]



def testNumpyTypeCoercion():
    import numpy as np
    t = ms.toTable("a", [np.int32(1)])
    t.info()
    assert t.colTypes == [int], t.colTypes
    t = ms.toTable("a", [None, np.int32(1)])
    t.info()
    assert t.colTypes == [int], t.colTypes

    t.addColumn("b", np.int32(1))
    assert t.colTypes == [int, int], t.colTypes
    t.replaceColumn("b", [None, np.int32(1)])
    assert t.colTypes == [int, int], t.colTypes

    t.replaceColumn("b", np.int64(1))
    assert t.colTypes == [int, int], t.colTypes
    t.replaceColumn("b", [None, np.int64(1)])
    assert t.colTypes == [int, int], t.colTypes

    t.replaceColumn("b", np.float32(1.0))
    assert t.colTypes == [int, float], t.colTypes
    t.replaceColumn("b", [None, np.float32(1.0)])
    assert t.colTypes == [int, float], t.colTypes

    t.replaceColumn("b", np.float64(2.0))
    assert t.colTypes == [int, float], t.colTypes
    t.replaceColumn("b", [None, np.float64(2.0)])
    assert t.colTypes == [int, float], t.colTypes

def testApplyUfun():
    import numpy
    t = ms.toTable("a", [None, 2.0, 3])

    print numpy.log
    t.addColumn("log", t.a.apply(numpy.log))
    assert t.colTypes == [ float, float], t.colTypes


def testNonBoolean():
    t = ms.toTable("a", [])
    try:
        not t.a
    except:
        pass
    else:
        raise Exception()

def testIllegalRows():
    try:
        t = Table(["a","b"], [float,float], ["%f", "%f"], [(1,2)])
    except Exception, e:
        assert "not all rows are lists" in str(e), str(e)
    else:
        pass

    import adducts
    adducts.all.toTable()



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


    t = Table(names, [float]*len(names), [], circumventNameCheck=True)
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
    r = t.a.max()
    assert r == 3
    assert t.a.min() == 2
    assert t.a.mean() == 2.5
    assert t.a.std() == 0.5

    assert t.a.hasNone(), t.a.hasNone()
    assert t.a.len() == 3, t.a.len()
    assert t.a.countNone() == 1, t.a.countNone()

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

    assert (t.a+t.c).values == [None, None , 4]
    assert (t.a+t.c).sum() == 4
    apc = (t.a+t.c).toTable("a_plus_c")
    assert apc.colNames == ["a_plus_c"]
    assert apc.colTypes == [int]
    assert apc.a_plus_c.values == [ None, None , 4]

    assert (apc.a_plus_c - t.a).values == [None, None, 1]

    # column from other table !
    t.addColumn("apc", apc.a_plus_c)
    assert t.apc.values==[None, None, 4], t.apc.values

    # column from other table !
    t2 = t.filter(apc.a_plus_c)
    assert len(t2) == 1
    assert  t2.apc.values == [4]


def testAggregateOperation():
    t = ms.toTable("a", [ ], type_=int)

    t2 = t.aggregate(t.a.mean, "an", groupBy="a")
    assert len(t2) == 0
    assert t2.colTypes == [int, object]

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
    print t.sum.values
    assert t.sum.values == [None, 2, 2, 16, 16, 16, 16], t.sum.values
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


def testIndex():
    t = ms.toTable("a",[1,2,3,4,5])
    t.addColumn("b", [2, 0, 1, 5,6 ])
    t.sortBy("a")
    print t.primaryIndex
    a = t.a

    es = [a<=2, a <= 0, a<=5, a<=6]
    vs = [2, 0, 5 , 5 ]
    es += [a<2, a < 0, a<1, a<5,  a<6]
    vs += [1, 0, 0, 4, 5]
    es += [a >= 2, a  >=  0, a >= 1, a >= 5,  a >= 6]
    vs += [4, 5, 5, 1, 0]
    es += [a > 2, a > 0, a>-2,  a > 1, a > 5,  a > 6]
    vs += [3, 5, 5, 4, 0, 0]

    assert len(es) == len(vs)

    for e,v in zip(es, vs):
        print e, v
        assert len(t.filter(e)) == v, len(t.filter(e))

    t2 = t.copy()
    assert t.join(t2, t.b < t2.a).a__0.values == [3, 4, 5, 1, 2, 3, 4, 5, 2, 3,4, 5]
    assert t.join(t2, t.b > t2.a).a__0.values == [ 1,1,2,3,4,1,2,3,4,5]
    assert t.join(t2, t.b <= t2.a).a__0.values == [ 2,3,4,5,1,2,3,4,5,1,2,3,4,5,5]
    assert t.join(t2, t.b >= t2.a).a__0.values == [ 1,2,1,1,2,3,4,5,1,2,3,4,5]

    assert t.join(t2, t.b == t2.a).a__0.values == [2,1,5]
    assert t.join(t2, t.b != t2.a).a__0.values == [1,3,4,5,1,2,3,4,5,2,3,4,5,1,2,3,4,1,2,3,4,5]


def testBools():
    t = ms.toTable("bool", [True, False, True, None])
    assert t.bool.sum() == 2
    assert t.bool.max() == True, t.bool.max()
    assert t.bool.min() == False, t.bool.min()

    t.addColumn("int", [1,2,3,4])
    t.addColumn("float", [1.0,2,3,4])
    t.addColumn("int_bool", (t.bool).thenElse(t.bool, t.int))

    # test coercion (bool, int) to int:
    assert t.int_bool.values == [ 1, 2, 1, None ]
    t.addColumn("int_float", (t.bool).thenElse(t.int, t.float))
    assert t.int_float.values == [ 1.0, 2.0, 3.0, None ], t.int_float.values

    t.addColumn("bool_float", (t.bool).thenElse(t.bool, t.float))
    assert t.bool_float.values == [ 1.0, 2.0, 1.0, None ]


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


def testLogics():
    t = ms.toTable("a", [True, False])
    t.addColumn("nota", ~t.a)
    t.addColumn("true", t.a | True)
    t.addColumn("false", t.a & False)

    assert t.colTypes == 4* [bool]

    assert len(t.filter(t.a & t.nota)) == 0
    assert len(t.filter(t.a | t.true)) == 2
    assert len(t.filter(t.a ^ t.nota)) == 2
    assert len(t.filter(t.a ^ t.a)) == 0

    bunch = t.get(t.rows[0])
    assert bunch.a == True
    assert bunch.nota == False
    assert bunch.true == True
    assert bunch.false == False


def testAppend():
    t = ms.toTable("a",[1,2])
    t2 = t.copy()
    t.append(t2, [t2, t2], (t2,))
    assert len(t) == 10
    assert t.a.values == [1,2]*5




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
