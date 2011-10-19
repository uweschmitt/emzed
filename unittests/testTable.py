#encoding: utf-8

from libms.DataStructures import Table, FeatureTable, PeakMap
import numpy as np
import pickle, copy

def testRunnerTable():
    
    #build table
    names="int long float str object array".split()
    types = [int, long, float, str, object, np.ndarray ]
    formats = [ "%3d", "%d", "%.3f", "%s", "%r", "'array(%r)' % o.shape" ]
    
    row1 = [ 1, 12323L, 1.14, "hi", { 1: 1 },  np.array((1,2,3)) ]
    row2 = [ 2, 22323L, 2.14, "hi2", [2,3,], np.array(((2,3,4),(1,2,3))) ]
    row3 = [ 3, 32323L, 3.14, "hi3", (3,) , np.array(((3,3,4,5),(1,2,3,4))) ]

    rows = [row1, row2, row3]
    t=Table(names, types, rows, formats, "testtabelle", meta=dict(why=42))

    run(t, names, [row1, row2, row3])
    # test pickle
    t = pickle.loads(pickle.dumps(t))
    run(t, names, [row1, row2, row3])

    #test subtable
    ts = t[0:3]
    assert isinstance( ts  , Table)
    assert len(ts)==3
    run(ts, names, [row1, row2, row3])


def run(t, colnames, rows): 

    t = copy.deepcopy(t) # prohibit changes  

    tn = t.extractRows([1,2])
    assert len(tn) == 2

    assert t.get(0,"int") == rows[0][0]
    assert t.get(0,"long") == rows[0][1]

    for i, name in enumerate(colnames):
        assert t.getIndex(name)  == i


    #test indexint
    assert isinstance(t[:1], Table)  # list means row
    assert len(t[:1])==1  

 

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

    assert t.get(0, "int") == rows[-1][0]
    assert t.get(1, "int") == rows[-2][0]
    assert t.get(2, "int") == rows[-3][0]

    assert t.get(0, "long") == rows[-1][1]
    assert t.get(0, "float") == rows[-1][2]
    assert t.get(0, "str") == rows[-1][3]
    assert t.get(0, "object") == rows[-1][4]
    assert t.get(0, "array").shape == rows[-1][5].shape

    # restrct cols
    tn = t.extractColumns( ["int", "long"])
    assert len(tn.colNames) == 2, len(t.colNames)
    assert len(tn.colTypes) == 2
    assert len(tn.colFormats) == 2

    assert len(tn) == len(t)

    assert tn.meta["why"] == 42
    assert tn.title == "testtabelle"


    
def testRunnerFeatureTable():
    
    #build table
    names="mz mzmin mzmax rt rtmin rtmax a b c".split()
    types = [float] * 6  + [ str, str, str ]
    formats = [ "%.2f" ] * 6  + [ "%s", None, "len(o)" ]
    
    row1 = [ 2.0, 1.0, 3.0, 20.0, 10.0, 30.0,  "aaa", "bbb", "ccc" ]
    row2 = [ 3.0, 2.0, 4.0, 30.0, 20.0, 40.0,  "aa", "bb", "cc" ]

    rows = [row1, row2]


    ds = PeakMap([])
    print ds
    print ds.meta

    t=FeatureTable(ds, names, types, rows, formats, "testtabelle", meta=dict(why=42))

    print t.ds.meta
    run2(t, names)
    print t.ds.meta
    # test pickle
    dat = pickle.dumps(t)
    t = pickle.loads(dat)
    print t.ds.meta
    run2(t, names)

    #test subtable
    ts = t[0:2]
    assert isinstance( ts  , Table)
    assert len(ts)==2
    run2(ts, names)


def run2(t, colnames): 

    t = copy.deepcopy(t) # prohibit changes  
    print t.ds.meta

    for i, name in enumerate(colnames):
        assert t.getIndex(name)  == i

    #test indexint
    assert isinstance(t[:1], Table)  # list means row
    assert len(t[:1])==1  


    # test iteration
    content = []
    for row in t:
        for (cell, formatter) in zip(row, t.colFormatters):
            content.append( formatter(cell))
        break

    # test formatting
    assert content[0] == "2.00"
    assert content[-2] == None
    assert content[-1] == 3

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

    t.sortBy("mz", ascending=False)

    assert t.get(0, "mz") == 3.0, t.get(0,"mz")
    assert t.get(1, "mz") == 2.0, t.get(1,"mz")

    assert t.get(0, "mzmin") == 2.0, t.get(0, "mzmin")
    assert t.get(0, "mzmax") == 4.0, t.get(0, "mzmax")

    # restrct cols
    ex = None
    try:
        tn = t.extractColumns("a b c".split())
    except Exception, e:
        ex = e
    assert ex is not None

    tn = t.extractColumns("rt rtmin rtmax mz mzmin mzmax".split())
    assert len(tn.colNames) == 6, len(t.colNames)
    assert len(tn.colTypes) == 6
    assert len(tn.colFormats) == 6

    assert len(tn) == len(t)

    assert tn.meta["why"] == 42
    assert tn.title == "testtabelle"

    assert tn.getIndex("rt") == 0
    assert tn.getIndex("mzmax") == 5

    
    
        

    

        
    
        

    

        


    

    
    

    
