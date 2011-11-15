#encoding: utf-8

from libms.DataStructures import Table
import ms
import numpy as np
import pickle, copy, os, re, sys
import StringIO
import difflib

def testRunnerTable():

    #build table
    names="int long float str object array".split()
    types = [int, long, float, str, object, np.ndarray,]
    formats = [ "%3d", "%d", "%.3f", "%s", "%r", "'array(%r)' % o.shape" ]

    row1 = [ 1, 12323L, 1.0, "hi", { 1: 1 },  np.array((1,2,3)) ]
    row2 = [ 2, 22323L, 2.0, "hi2", [2,3,], np.array(((2,3,4),(1,2,3))) ]
    row3 = [ 3, 32323L, 3.0, "hi3", (3,) , np.array(((3,3,4,5),(1,2,3,4))) ]

    rows = [row1, row2, row3]
    t=Table(names, types, formats, rows, "testtabelle", meta=dict(why=42))

    run(t, names, [row1, row2, row3])
    # test pickle
    t = pickle.loads(pickle.dumps(t))
    run(t, names, [row1, row2, row3])
    ms.storeTable(t, "temp_output/test.table")
    t = ms.loadTable("temp_output/test.table")
    run(t, names, [row1, row2, row3])


def run(t, colnames, rows):
    t = copy.deepcopy(t) # prohibit changes
    ixs = set()
    for i, name in enumerate(colnames):
        ixs.add(t.getIndex(name))
    assert not None in ixs
    assert len(ixs) == len(colnames)

    # test iteration
    content = []
    for row in t:
        for (cell, formatter) in zip(row, t.colFormatters):
            content.append( formatter(cell))
        break

    # test formatting
    assert content[0] == "  1"
    assert content[1] == "12323"
    assert content[2] == "1.000"
    assert content[3] == "hi"
    assert content[4] == repr({1:1})
    assert content[5] == "array(3)"

    assert set(t.getVisibleCols()) == { 'int', 'long', 'float', 'str',
                                        'object', 'array' }

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
    tn = t.extractColumns( ["int", "long"])
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

    tn.addConstantColumn('x', str, '%s', 'hi')
    assert set(tn.getVisibleCols()) == { 'iii', 'long', 'id', 'x' }
    assert tn.colNames[-1]=="x"

    assert list(tn.x) == ["hi"]*len(tn)

    before = set(os.listdir("temp_output"))
    tn.storeCSV("temp_output/x.csv")
    tn.storeCSV("temp_output/x.csv")
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

    tn.addColumn("computed", tn.long / (tn.iii + 1))
    tn.addColumn("squared", tn.iii * tn.iii)
    assert list(tn.getColumn("computed").values ) == [8080, 7441, 6161]
    assert list(tn.getColumn("squared").values ) == [9, 4, 1]

    tn.replaceColumn("squared", tn.squared+1)
    assert list(tn.getColumn("squared").values ) == [10, 5, 2]
    assert len(tn.colNames)  == 6

    tn.dropColumn("computed")
    tn.dropColumn("squared")
    assert tn.colNames == [ "id", "iii", "long", "x"]
    assert len(tn) == 3




