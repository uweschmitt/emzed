#encoding: utf-8

from libms.DataStructures.Table import Table
import ms
import numpy as np
import pickle, os, re

def testRunnerTable():

    #build table
    names="int long float str object array".split()
    types = [int, long, float, str, object, np.ndarray,]
    formats = [ "%3d", "%d", "%.3f", "%s", "%r", "'array(%r)' % (o.shape,)" ]

    row1 = [ 1, 12323L, 1.0, "hi", { 1: 1 },  np.array((1,2,3)) ]
    row2 = [ 2, 22323L, 2.0, "hi2", [2,3,], np.array(((2,3,4),(1,2,3))) ]
    row3 = [ 3, 32323L, 3.0, "hi3", (3,) , np.array(((3,3,4,5),(1,2,3,4))) ]

    rows = [row1, row2, row3]
    t=Table(names, types, formats, rows, "testtabelle", meta=dict(why=42))


    run(t, names, [row1, row2, row3])
    # test pickle
    dat = pickle.dumps(t)
    t = pickle.loads(dat)
    run(t, names, [row1, row2, row3])
    ms.storeTable(t, "temp_output/test.table")
    t = ms.loadTable("temp_output/test.table")
    run(t, names, [row1, row2, row3])


def run(t, colnames, rows):
    t = t.copy()
    ixs = set()
    for i, name in enumerate(colnames):
        ixs.add(t.getIndex(name))
    assert not None in ixs
    assert len(ixs) == len(colnames)

    # test iteration
    content = []
    for row in t.rows:
        for (cell, formatter) in zip(row, t.colFormatters):
            content.append( formatter(cell))
        break

    # test formatting
    assert content[0] == "  1"
    assert content[1] == "12323"
    assert content[2] == "1.000"
    assert content[3] == "hi"
    assert content[4] == repr({1:1})
    assert content[5] == "array((3,))", content[5]

    assert set(t.getVisibleCols()) == { 'int', 'long', 'float', 'str',
                                        'object', 'array' }

    

    tn = t.filter(t.str.contains("hi"))
    assert len(tn) == 3
    tn = t.filter(~ t.str.contains("hi"))
    assert len(tn) == 0

    tn = t.filter(t.str.contains("2"))
    assert len(tn) == 1



    # test requireColumn
    for name in colnames:
        t.requireColumn(name)

    ex = None
    try:
        t.requireColumn("asdfklödsflkjaldfkjaösdlfjalödjf")
    except Exception, e:
        ex = e
    assert ex is not None

    # test other fields
    assert t.meta["why"] == 42
    assert t.title == "testtabelle"

    t.sortBy("int", ascending=False)

    # restrct cols
    tn = t.extractColumns("int", "long")
    assert len(tn.colNames) == 2, len(t.colNames)
    assert len(tn.colTypes) == 2
    assert len(tn.colFormats) == 2

    assert len(tn) == len(t)

    assert tn.meta["why"] == 42
    assert tn.title == "testtabelle"

    tn.addEnumeration()
    assert set(tn.getVisibleCols()) == { 'int', 'long', 'id' }
    assert tn.colNames[0]=="id"
    assert list(tn.id) == range(len(t))

    tn.renameColumns(int='iii')
    assert set(tn.getVisibleCols()) == { 'iii', 'long', 'id' }

    tn.addColumn('x', 'hi', str, '%s')
    assert set(tn.getVisibleCols()) == { 'iii', 'long', 'id', 'x' }
    assert tn.colNames[-1]=="x"

    assert list(tn.x) == ["hi"]*len(tn)

    before = set(os.listdir("temp_output"))
    tn.storeCSV("temp_output/x.csv")

    tnre  = ms.loadCSV("temp_output/x.csv")
    assert len(tnre) == len(tn)
    assert tnre.colNames == tn.colNames
    assert tnre.id.values == tn.id.values
    assert tnre.iii.values == tn.iii.values
    assert tnre.long.values == tn.long.values
    assert tnre.x.values == tn.x.values



    tn.storeCSV("temp_output/x.csv", onlyVisibleColumns=False)
    after = set(os.listdir("temp_output"))
    # file written twice !
    assert len(after-before) == 2
    for n in after-before:
        # maybe we have some x.csv.? from previous run of this
        #function so we can not assume that we find x.csv and 
        #x.csv.1
        assert re.match("x.csv(.\d+)?", n)

    ex = None
    try:
        # wrong file extension
        tn.storeCSV("temp_output/x.dat")
    except Exception, e:
        ex = e

    assert ex != None

    # computed by exrpression
    tn.addColumn("computed", tn.long / (tn.iii + 1))
    # computed by callback:
    tn.addColumn("squared", lambda t,r,n: t.get(r, "iii")**2)


    assert list(tn.getColumn("computed").values ) == [8080, 7441, 6161]
    assert list(tn.getColumn("squared").values ) == [9, 4, 1]


    tn.replaceColumn("squared", tn.squared+1)
    assert list(tn.getColumn("squared").values ) == [10, 5, 2]
    assert len(tn.colNames)  == 6

    tx  = tn.copy()
    tx.dropColumns("squared", "computed")
    assert tx.colNames == ["id", "iii", "long", "x"]
    assert len(tx) == 3

    tn.dropColumns("computed", "squared")
    assert tn.colNames == ["id", "iii", "long", "x"]
    assert len(tn) == 3

    tn.dropColumn("id")
    tn.dropColumn("x")
    t2 = tn.copy()
    res = tn.leftJoin(t2, tn.iii == tn.long)
    assert len(res) == len(t2)
    res = tn.leftJoin(t2, tn.iii == tn.iii)
    assert len(res) == len(t2)**2
    res = tn.leftJoin(t2, (tn.iii == tn.iii) & (t2.long==32323))
    assert len(res) == len(t2)

    res = tn.join(t2, tn.iii == tn.long)
    assert len(res) == 0
    res = tn.join(t2, tn.iii == tn.iii)
    assert len(res) == len(t2)**2, len(res)
    res = tn.join(t2, (tn.iii == tn.iii) & (t2.long==32323))
    assert len(res) == len(t2), len(res)

    tx = tn.filter(tn.iii.isIn([1,4]))
    tx._print()
    assert len(tx) == 1
    assert tx.iii.values == [1]
    
    tn.addColumn("li", [1,2,3])
    assert len(tn) == 3
    assert len(tn.colNames) == 3
    assert "li" in tn.colNames
    
    tn.addRow([1, 1, 1])
    assert len(tn) == 4

    ex = None
    try:
        tn.addRow([1,2,3,2])
    except Exception, e:
        ex = e
    assert ex is not None

    ex = None
    try:
        tn.addRow(["a",1,2])
    except Exception, e:
        ex = e
    assert ex is not None


def testSomePredicates():
    #build table
    names="int long float str object array".split()
    types = [int, long, float, str, object, np.ndarray,]
    formats = [ "%3d", "%d", "%.3f", "%s", "%r", "'array%r' % (o.shape,)" ]

    row1 = [ 1, 12323L, 1.0, "hi", { 1: 1 },  np.array((1,2,3)) ]
    row2 = [ 2, 22323L, 2.0, "hi2", [2,3,], np.array(((2,3,4),(1,2,3))) ]
    row3 = [ 3, 32323L, 3.0, "hi3", (3,) , np.array(((3,3,4,5),(1,2,3,4))) ]

    rows = [row1, row2, row3]
    t=Table(names, types, formats, rows, "testtabelle", meta=dict(why=42))

    tn = t.filter((t.int+t.float).inRange(-1, 2))
    assert len(tn) == 1
    assert tn.get(tn.rows[0], "int") == 1

    tn = t.filter(t.float.approxEqual(1.0, t.int/10))
    assert len(tn) == 1
    assert tn.get(tn.rows[0], "int") == 1



def testDoubleColumnames():
    ex = None
    try:
        colnames = ["col0", "col0", "col1", "col1", "col2"]
        Table(colnames, []*5, []*5)
    except Exception, e:
        ex = e.message
    assert ex != None
    assert "multiple" in ex
    assert "col0" in ex
    assert "col1" in ex
    assert "col2" not in ex

def testDetectionOfUnallowdColumnNames():
    ex = None
    try:
        Table(["__init__"], [int],["%d"])
    except Exception, e:
        ex = e.message
    assert ex != None
    assert "not allowed" in ex
    assert "__init__" in ex


def testWithEmtpyTablesAndTestColnameGeneration():
    e = ms.toTable("x", [])
    f = ms.toTable("y", [])
    g = ms.toTable("z", [1])

    assert len(e.filter(e.x == 0)) == 0
    t1 = e.join(f, f.y == e.x)
    assert len(t1) == 0
    assert t1.colNames == ["x", "y_1"]
    t1 = e.join(g, g.z == e.x)
    assert len(t1) == 0
    assert t1.colNames == ["x", "z_1"]
    t1 = g.join(e, e.x == g.z)
    assert len(t1) == 0
    assert t1.colNames == ["z", "x_1"]

    t1 = e.leftJoin(f, f.y == e.x)
    assert len(t1) == 0
    assert t1.colNames == ["x", "y_1"]
    t1 = e.leftJoin(g, g.z == e.x)
    assert len(t1) == 0
    assert t1.colNames == ["x", "z_1"]
    t1 = g.leftJoin(e, e.x == g.z)
    assert len(t1) == 1
    assert t1.colNames == ["z", "x_1"]
    assert t1.rows[0] ==  [1, None]

    t2 = t1.leftJoin(f, f.y == t1.x_1)
    assert t2.colNames ==["z", "x_1", "y_2"]
    assert len(t2) == 1


class ExceptionTester(object):

    def __init__(self, *expected):
        self.expected = expected

    def __enter__(self):
        return self

    def __exit__(self, *a):
        assert a[0] in self.expected
        return True # suppress exceptoin

def testWithNoneValues():
    t = ms.toTable("i", [1,2,None])
    with ExceptionTester(Exception):
        t.filter(t.i >=1)._print()
    with ExceptionTester(Exception):
        t.filter(t.i <=1)._print()
    with ExceptionTester(Exception):
        t.filter(t.i >1)._print()
    with ExceptionTester(Exception):
        t.filter(t.i <1)._print()

    assert len(t.filter(t.i == None)) == 1
    assert len(t.filter(t.i != None)) == 2

    t.addColumn("b", [2,3,None])
    assert t.colNames == ["i", "b"]
    t.replaceColumn("b", t.b+1)

    assert t.colNames == ["i", "b"]

    t.addRow([None, None])
    t.addRow([3, None])
    t.addRow([3, 3.0])
    assert t.b.values == [ 3, 4, None, None, None, 3]

    # check order
    t.replaceColumn("i", t.i)
    assert t.colNames == ["i", "b"]

def testSomeExpressions():
    t = ms.toTable("mf", ["Ag", "P", "Pb", "P3Pb", "PbP"])
    tn = t.filter(t.mf.containsElement("P"))
    assert len(tn) == 3
    tn = t.filter(t.mf.containsElement("Pb"))
    assert len(tn) == 3


def testIfThenElse():
    t = Table(["a", "b", "c"], [str, int, int], ["%s", "%d", "%d"],[])
    t.rows.append(["0", 1, 2])
    t.rows.append([None, 2, 1])
    t._print()
    t.addColumn("x", (t.a == None).thenElse(t.b, t.c))
    assert t.colNames==["a", "b", "c", "x"]
    t._print()


def testDynamicColumnAttributes():
    t = Table(["a", "b", "c"], [str, int, int], ["%s", "%d", "%d"],[])
    t.a
    t.b
    t.c
    assert len(t.a.values) == 0
    assert len(t.b.values) == 0
    assert len(t.c.values) == 0

    t.renameColumns(a="aa")
    assert "a" not in t.colNames
    assert "aa"  in t.colNames
    t.aa
    try:
        t.a
        raise Exception("t.a should be deteted")
    except:
        pass

    col = pickle.loads(pickle.dumps(t.aa))
    assert len(col.values) == 0

    t.dropColumn("aa")
    assert "aa" not in t.colNames
    try:
        t.aa
        raise Exception("t.aa should be deteted")
    except:
        pass


def testSplitBy():
    t = ms.toTable("a", [1,1,3,4])
    t.addColumn("b", [1,1,3,3])
    t.addColumn("c", [1,2,1,4])
    t._print()
    subts = t.splitBy("a")
    assert len(subts) == 3
    res = ms.mergeTables(subts)
    assert len(res) == len(t)
    subts[0]._print()
    assert res.a.values == t.a.values
    assert res.b.values == t.b.values
    assert res.c.values == t.c.values

    subts = t.splitBy("a", "c")
    assert len(subts) == 4
    res = ms.mergeTables(subts)
    assert res.a.values == t.a.values
    assert res.b.values == t.b.values
    assert res.c.values == t.c.values

def testConstantColumn():
    t = ms.toTable("a",[1,2,3])
    t.addConstantColumn("b", dict())
    assert len(set(id(x) for x in t.b.values)) == 1



