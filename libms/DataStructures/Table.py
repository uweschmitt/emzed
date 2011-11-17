import pyOpenMS as P
import operator, copy, os, itertools, re, numpy, cPickle, sys
from   ExpressionTree import Node, Column
import numpy as np

_standardFormats = { int: "%d", float : "%.2f", str: "%s" }

class _CmdLineProgress(object):

    def __init__(self, imax, step=5):
        self.imax = imax
        self.step = step
        self.last = 0

    def progress(self, i):
        percent = int(100.0 * (i+1) / self.imax)
        if percent >= self.last+self.step:
            print percent,
            sys.stdout.flush()
            self.last = percent

def _commonTypeOfColumn(col):
    if isinstance(col, np.ndarray):
        return col.dtype
    types = set( type(c) for c in col )
    if str in types:
        return str
    if float in types:
        return float
    if int in types:
        return int
    raise Exception("do not know how to find common type for %r" % types)


def _formatter(f):
    """ helper, is toplevel for supporting pickling of Table """

    if f is None:
        def format(s):
            return None
    elif f.startswith("%"):
        def format(s, f=f):
            return "-" if s is None else f % s
    else:
        def format(s, f=f):
            return "-" if s is None else eval(f, globals(), dict(o=s))
    return format


class Table(object):

    def __init__(self, colNames, colTypes, colFormats, rows=None, title=None,
                       meta=None):
        assert len(colNames) == len(colTypes)
        if rows is not None:
            for row in rows:
                assert len(row) == len(colNames)
        else:
            rows = []
        self.colNames = list(colNames)
        self.colTypes = list(colTypes)
        self.rows     = rows
        self.colFormats = [None if f=="" else f for f in colFormats]

        self.colIndizes = dict((n, i) for i, n in enumerate(colNames))
        self.title = title
        self.meta = copy.copy(meta) if meta is not None else dict()
        self.primaryIndex = {}
        self.setupFormatters()
        self.updateIndices()
        self.emptyColumnCache()
        self.name = str(self)

    def emptyColumnCache(self):
        self.columnCache = dict()

    def updateIndices(self):
        self.colIndizes = dict((n, i) for i, n in enumerate(self.colNames))

    def getVisibleCols(self):
        return [n for (n, f) in zip (self.colNames, self.colFormats)\
                              if f is not None ]

    def setupFormatters(self):
        self.colFormatters = [_formatter(f) for f in self.colFormats ]

    def __getattr__(self,name):
        if name in self.colNames:
            return self.getColumn(name)
        raise AttributeError("%s has no attribute %s" % (self, name))

    def getColumn(self, name):
        if name in self.columnCache:
            return self.columnCache[name]
        ix = self.getIndex(name)
        values = [ row[ix] for row in self.rows ]
        rv = Column(self, name, values)
        self.columnCache[name] = rv
        return rv

    def __getstate__(self):
        """ for pickling. """
        dd = self.__dict__.copy()
        # self.colFormatters can not be pickled
        del dd["colFormatters"]
        # for effiency:
        del dd["columnCache"]
        return dd

    def __setstate__(self, dd):
        self.__dict__ = dd
        self.setupFormatters()
        self.emptyColumnCache()

    def __iter__(self):
        return iter(self.rows)

    def hasColumn(self, name):
        return name in self.colNames

    def hasColumns(self, *names):
        return all(self.hasColumn(n) for n in names)

    def requireColumn(self, name):
        if not name in self.colNames:
            raise Exception("column %r required" % name)
        return self

    def getIndex(self, colName):
        idx = self.colIndizes.get(colName, None)
        if idx is None:
            raise Exception("colname %s not in table" % colName)
        return idx

    def get(self, row, colName):
        return row[self.getIndex(colName)]

    def getColumnCtx(self, needed):
        names = [ n for (t,n) in needed if t==self ]
        return dict((n, (self.getColumn(n).getValues(),
                         self.primaryIndex.get(n))) for n in names)

    def addEnumeration(self, colname="id"):
        """ adds enumerated column as first column to table inplace """

        if colname in self.colNames:
            raise Exception("column with name %s already exists")
        self.colNames.insert(0, colname)
        self.colTypes.insert(0, int)
        if len(self)>99999:
            fmt = "%6d"
        elif len(self) > 9999:
            fmt = "%5d"
        elif len(self) > 999:
            fmt = "%4d"
        elif len(self) > 99:
            fmt = "%3d"
        elif len(self) > 9:
            fmt = "%2d"
        else:
            fmt = "%d"
        fmt = "%d"
        self.colFormats.insert(0, fmt)
        for i, r in enumerate(self.rows):
            r.insert(0, i)
        self.setupFormatters()
        self.updateIndices()

    def sortBy(self, colName, ascending=True):
        idx = self.colIndizes[colName]
        self.rows.sort(key = operator.itemgetter(idx), reverse=not ascending)
        if ascending:
            self.primaryIndex = {colName: True}
        else:
            self.primaryIndex = {}

    def addConstantColumn(self, name, type_, format, value=None):
        # HIER MIT EXPRESSION !
        for row in self.rows:
            row.append(value)
        self.colNames.append(name)
        self.colTypes.append(type_)
        self.colFormats.append(format)
        self.setupFormatters()
        self.updateIndices()

    def extractColumns(self, names):
        indices = [self.getIndex(name)  for name in names]
        types = [ self.colTypes[i] for i in indices ]
        formats = [self.colFormats[i] for i in indices]
        rows = [[row[i] for i in indices] for row in self.rows]
        return Table(names, types, formats, rows, self.title, self.meta.copy())

    def renameColumns(self, **kw):
        for k in kw.keys():
            if k not in self.colNames:
                raise Exception("colum %s does not exist" % k)
        self.colNames = [ kw.get(n,n) for n in self.colNames]
        self.emptyColumnCache()
        self.updateIndices()

    def __len__(self):
        return len(self.rows)

    def storeCSV(self, path):
        if not os.path.splitext(path)[1].upper()==".CSV":
            raise Exception("%s has wrong filentype extension" % path)
        it = itertools
        for p in it.chain([path], ( "%s.%d" % (path, i) for i in it.count(1))):
            if not os.path.exists(p):
                print "write ", p
                with file(p, "w") as fp:
                    print >> fp, "; ".join(self.colNames)
                    for row in self.rows:
                        print >> fp, "; ".join(map(str, row))
                break

    def store(self, path, forceOverwrite=False):
        if not os.path.splitext(path)[1].upper()==".TABLE":
            raise Exception("%s has wrong extension, need .table" % path)
        if not forceOverwrite and os.path.exists(path):
            raise Exception("%s exists. You may use forceOverwrite=True" % path)
        with open(path, "wb") as fp:
            cPickle.dump(self, fp)

    @staticmethod
    def load(path):
        with open(path, "rb") as fp:
            return cPickle.load(fp)


    def buildEmptyClone(self):
        return Table(self.colNames, self.colTypes, self.colFormats, [],
                     self.title, self.meta.copy())

    def dropColumn(self, name):
        ix = self.getIndex(name)
        del self.colNames[ix]
        del self.colFormats[ix]
        del self.colTypes[ix]
        for row in self.rows:
            del row[ix]
        self.updateIndices()
        self.setupFormatters()
        self.emptyColumnCache()

    def addColumn(self, name, expr, type=None, format=None):
        if name in self.colNames:
            raise Exception("column with name %s already exists" % name)
        ctx = { self: self.getColumnCtx(expr.neededColumns()) }
        values, _ = expr.eval(ctx)
        if type is None:
            type = _commonTypeOfColumn(values)
        if format is None:
            format = _standardFormats.get(type)

        self.colNames.append(name)
        self.colTypes.append(type)
        self.colFormats.append(format)
        for row, v in zip(self.rows, values):
            row.append(v)

        self.setupFormatters()
        self.updateIndices()

    def replaceColumn(self, name, expr, format=None):
        ix = self.getIndex(name)
        ctx = { self: self.getColumnCtx(expr.neededColumns()) }
        values, _ = expr.eval(ctx)
        t = _commonTypeOfColumn(values)
        f = format if format is not None else _standardFormats.get(t)

        self.colNames[ix] = name
        self.colTypes[ix] = t
        self.colFormats[ix] = f
        for row, v in zip(self.rows, values):
            row[ix] = v
        self.setupFormatters()
        self.updateIndices()
        self.emptyColumnCache()

    def unique(self):
        raise Exception("does not work")
        rv = self.buildEmptyClone()
        # rows as tuples, set does not like unhashable lists as elements
        rows = set( tuple(row) for row in self.rows )
        rv.rows = list(rows)
        return rv

    def filter(self, expr, debug = False):
        assert isinstance(expr, Node)
        if debug:
            print "#", expr

        ctx = { self: self.getColumnCtx(expr.neededColumns()) }
        flags, _ = expr.eval(ctx)
        rv = self.buildEmptyClone()
        rv.rows = [ self.rows[n] for n, i in enumerate(flags) if i ]
        return rv

    def join(self, t, expr, debug = False):
        assert isinstance(t, Table)
        assert isinstance(expr, Node)
        if debug:
            print "# %s.join(%s, %s)" % (self.name, t.name, expr)
        tctx = t.getColumnCtx(expr.neededColumns())

        cmdlineProgress = _CmdLineProgress(len(self))
        rows = []
        for ii, r1 in enumerate(self.rows):
            r1ctx = dict((n, (v, None)) for (n,v) in zip(self.colNames, r1))
            ctx = {self:r1ctx, t:tctx}
            flags,_ = expr.eval(ctx)
            rows.extend([ r1 + t.rows[n] for (n,i) in enumerate(flags) if i])
            cmdlineProgress.progress(ii)

        table = self._buildJoinTable(t)
        table.rows = rows
        return table

    def _buildJoinTable(self, t):

        names1 = self.colNames
        names2 = t.colNames
        colNames = []
        for name in names1:
            if name in names2:
                name = name+"_1"
            colNames.append(name)
        for name in names2:
            if name in names1:
                name = name+"_2"
            colNames.append(name)
        colFormats = self.colFormats + t.colFormats
        colTypes = self.colTypes + t.colTypes
        title = "%s vs %s" % (self.title, t.title)
        meta = {self: self.meta.copy(), t: t.meta.copy()}
        return Table(colNames, colTypes, colFormats, [], title, meta)

    def leftJoin(self, t, expr, debug = False, progress=True):
        assert isinstance(t, Table)
        assert isinstance(expr, Node)
        if debug:
            print "# %s.leftJoin(%s, %s)" % (self.name, t.name, expr)
        tctx = t.getColumnCtx(expr.neededColumns())

        filler = [None] * len(t.colNames)
        cmdlineProgress = _CmdLineProgress(len(self))

        rows = []
        for ii, r1 in enumerate(self.rows):
            r1ctx = dict((n, (v, None)) for (n,v) in zip(self.colNames, r1))
            ctx = {self:r1ctx, t:tctx}
            flags,_ = expr.eval(ctx)
            if numpy.any(flags):
                rows.extend([r1 + t.rows[n] for (n,i) in enumerate(flags) if i])
            else:
                rows.extend([r1 + filler])
            cmdlineProgress.progress(ii)


        table = self._buildJoinTable(t)
        table.rows = rows
        return table


    def _print(self, w=12):
        #inner method is private, else the object can not be pickled !
        def _p(vals, w=w):
            expr = "%%-%ds" % w
            for v in vals:
                print (expr % v),

        _p(self.colNames)
        print
        _p(re.match("<type '((\w|[.])+)'>|(\w+)", str(n)).groups()[0]  or str(n)
                                                   for n in self.colTypes)
        print
        _p(["------"] * len(self.colNames))
        print
        for row in self.rows:
            _p(row)
            print


def toOpenMSFeatureMap(table):
    table.requireColumn("mzmin")
    table.requireColumn("mzmax")
    table.requireColumn("mz")
    table.requireColumn("rt")
    table.requireColumn("rtmax")
    table.requireColumn("rtmax")

    if "into" in table.colNames:
        iarea = table.getIndex("into")
    elif "area" in table.colNames:
        iarea = table.getIndex("area")
    else:
        print "features not integrated. I assume const intensity"
        iarea = None

    imz = table.getIndex("mz")
    irt = table.getIndex("rt")
    fm = P.FeatureMap()

    for row in table.rows:
        f = P.Feature()
        f.setMZ(row[imz])
        f.setRT(row[irt])
        if iarea is not None:
            f.setIntensity(row[iarea])
        else:
            f.setIntensity(1000.0)
        fm.push_back(f)
    return fm
