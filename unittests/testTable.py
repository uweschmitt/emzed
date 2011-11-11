#encoding: utf-8

from libms.DataStructures import Table
import numpy as np
import pickle, copy

def testRunnerTable():

    #build table
    names="int long float str object array".split()
    types = [int, long, float, str, object, np.ndarray,]
    formats = [ "%3d", "%d", "%.3f", "%s", "%r", "'array(%r)' % o.shape" ]

    row1 = [ 1, 12323L, 1.14, "hi", { 1: 1 },  np.array((1,2,3)) ]
    row2 = [ 2, 22323L, 2.14, "hi2", [2,3,], np.array(((2,3,4),(1,2,3))) ]
    row3 = [ 3, 32323L, 3.14, "hi3", (3,) , np.array(((3,3,4,5),(1,2,3,4))) ]

    rows = [row1, row2, row3]
    t=Table(names, types, formats, rows, "testtabelle", meta=dict(why=42))

    run(t, names, [row1, row2, row3])
    # test pickle
    t = pickle.loads(pickle.dumps(t))
    run(t, names, [row1, row2, row3])

    #TODO: filter instead of getitem with slice
    #test subtable
    #ts = t[0:3]
    #assert isinstance( ts  , Table)
    #assert len(ts)==3
    #run(ts, names, [row1, row2, row3])


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
    assert content[2] == "1.140"
    assert content[3] == "hi"
    assert content[4] == repr({1:1})
    assert content[5] == "array(3)"

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














