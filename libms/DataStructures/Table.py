import pyOpenMS as P
import operator, copy, os, itertools, re, numpy, cPickle, sys, inspect
from   ExpressionTree import Node, Column
import numpy as np
from   collections import Counter

standardFormats = { int: "%d", long: "%d", float : "%.2f", str: "%s" }
fms = "'%.2fm' % (o/60.0)"  # format seconds to floating point minutes

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

def commonTypeOfColumn(col):
    col = list(col)
    if isinstance(col, np.ndarray):
        dtype = col.dtype
        if dtype in [np.int8, np.int16, np.int32]:
            return int
        elif dtype == np.int64:
            return long
        else:
            return float

    types = set( type(c) for c in col )
    if str in types:
        return str
    if float in types:
        return float
    if int in types:
        return int
    if len(types) == 1:
        # unknown types as dict, object, ...
        return types.pop()
    raise Exception("do not know how to find common type for different types %r" % types)

def bestConvert(val):
    try:
        return int(val)
    except ValueError:
        try:
            return float(val)
        except ValueError:
            try:
                return float(val.replace(",",".")) # probs with comma
            except ValueError:
                return str(val)

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
    """
    A table holds rows of the same lenght. Each Column of the table has
    a *name*, a *type* and *format* information, which indicates how to render
    values in this column.
    Further a table has a title and meta information which is a dictionary.

    columntypes can be any python type.

    format can be:
         - a string interpolation string, eg "%.2f"
         - None, which supresses rendering of this column
         - python code which renders an object of name 'o', eg
           'str(o)+"x"'
    """

    def __init__(self, colNames, colTypes, colFormats, rows=None, title=None,
                       meta=None):

        if len(colNames) != len(set(colNames)):
            counts = Counter(colNames)
            multiples = [name for (name, count) in counts.items() if count>1]
            message = "multiple columns: " + ", ".join(multiples)
            raise Exception(message)


        assert len(colNames) == len(colTypes)
        if rows is not None:
            for row in rows:
                assert len(row) == len(colNames)
        else:
            rows = []
        self.colNames = list(colNames)
        self.updateIndices()

        self.colTypes = list(colTypes)

        if any(type(t) in (np.float32, np.float64) for t in colTypes):
            print "WARNING: using numpy floats instead of python floats "\
                  "is not a good idea.\nTable operations may crash"

        self.colFormats = [None if f=="" else f for f in colFormats]
        self.setupFormatters()

        self.rows = rows
        self.title = title
        self.meta = copy.copy(meta) if meta is not None else dict()

        self.primaryIndex = {}
        self.emptyColumnCache()
        self._name = str(self)

        self.editableColumns = set()

        # as we provide  access to colums via __getattr__, colnames must
        # not be in objects __dict__ and must not be name of member
        # functions:
        memberNames = [name for name, obj in inspect.getmembers(self)]
        for name in colNames:
            if name in self.__dict__ or name in memberNames:
                raise Exception("colName %s not allowed" % name)

    def addRow(self, row):
        assert len(row) == len(self.colNames)
        # check for conversion !
        for i, (v, t) in enumerate(zip(row, self.colTypes)):
            if t!= object:
                t(v)
            except:
                raise Exception("value %r in col %d can not be converted to "\
                                "type %s" % (v, i, t))
        self.rows.append(row)

    def isEditable(self, colName):
        return colName in self.editableColumns

    def emptyColumnCache(self):
        self.columnCache = dict()

    def updateIndices(self):
        self.colIndizes = dict((n, i) for i, n in enumerate(self.colNames))

    def getVisibleCols(self):
        """ returns a list with the names of the columns which are
            visible. that is: the corresponding format is not None """
        return [n for (n, f) in zip (self.colNames, self.colFormats)\
                              if f is not None ]

    def getFormat(self, colName):
        return self.colFormats[self.getIndex(colName)]

    def setFormat(self, colName, fmt):
        """ sets format of columns *colName* to format *fmt* """
        self.colFormats[self.getIndex(colName)] = fmt
        self.setupFormatters()

    def setupFormatters(self):
        self.colFormatters = [_formatter(f) for f in self.colFormats ]

    def __getattr__(self, name):
        if name in self.colNames:
            return self.getColumn(name)
        raise AttributeError("%s has no attribute %s" % (self, name))

    def getColumn(self, name):
        """ returns Column object for column *name*.
            to get the values of the colum you can use
            ``table.getColumn("index").values``
        """
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
        """ checks if column with given name *name* exists """
        return name in self.colNames

    def hasColumns(self, *names):
        """ checks if columns with given names exist """
        return all(self.hasColumn(n) for n in names)

    def requireColumn(self, name):
        """ throws exception if column with name *name* does not exist"""
        if not name in self.colNames:
            raise Exception("column %r required" % name)
        return self

    def getIndex(self, colName):
        """ gets the integer index of the column colName,
            eg you can use it as
            ``table.rows[0][table.getIndex("mz")]``
            """
        idx = self.colIndizes.get(colName, None)
        if idx is None:
            raise Exception("colname %s not in table" % colName)
        return idx

    def set(self, row, colName, value):
        """ sets *value* of column *colName* in a given *row*.

            usage: ``table.set(table.rows[0], "mz", 252.83332)``
        """
        ix = self.getIndex(colName)
        #expectedType = self.colTypes[ix]
        #assert isinstance(value, expectedType),\
               #"expect value of type %s" % expectedType
        row[ix] = value
        self.emptyColumnCache()

    def get(self, row, colName):
        """ returns value of column *colName* in a given *row*#

            usage: ``table.get(table.rows[0], "mz")``
        """
        return row[self.getIndex(colName)]

    def getColumnCtx(self, needed):
        names = [ n for (t,n) in needed if t==self ]
        return dict((n, (self.getColumn(n).getValues(),
                         self.primaryIndex.get(n))) for n in names)

    def addEnumeration(self, colname="id"):
        """ adds enumerated column as first column to table **inplace**.

            if *colname* is not given the colname is "id"

            Enumeration starts with zero
        """

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
        """
        sorts table in respect of column named *colName* **inplace**.
        *ascending* is boolean and tells if the values are sorted
        in ascending order or descending.

        This is important to build an internal index for faster queries
        with ``Table.filter``, ``Table.leftJoin`` and ``Table.join``.

        For building an internal index, ascending must be *True*, you
        can have only one index per table.
        """
        idx = self.colIndizes[colName]
        self.rows.sort(key = operator.itemgetter(idx), reverse=not ascending)
        if ascending:
            self.primaryIndex = {colName: True}
        else:
            self.primaryIndex = {}
        self.emptyColumnCache()


    def copy(self):
        """ returns a deep copy of the table """
        return copy.deepcopy(self)

    def extractColumns(self, *names):
        """extracts the given columnames and returns a new
           table with these colums, eg ``t.extractColumns("id", "name"))``
           """
        indices = [self.getIndex(name)  for name in names]
        types = [ self.colTypes[i] for i in indices ]
        formats = [self.colFormats[i] for i in indices]
        rows = [[row[i] for i in indices] for row in self.rows]
        return Table(names, types, formats, rows, self.title, self.meta.copy())

    def renameColumns(self, **kw):
        """renames colums **inplace**.
           So if you want to rename "mz_1" to "mz" and "rt_1"
           to "rt", ``table.renameColumns(mz_1=mz, rt_1=rt)``
        """
        for k in kw.keys():
            if k not in self.colNames:
                raise Exception("colum %s does not exist" % k)
        self.colNames = [ kw.get(n,n) for n in self.colNames]
        self.emptyColumnCache()
        self.updateIndices()

    def __len__(self):
        return len(self.rows)

    def storeCSV(self, path):
        """writes the table in .csv format. The *path* has to end with
           '.csv'.

           If the file allready exists, the routine tries names
           ``*.csv.1, *.csv.2, ...`` until a nonexisting file name is found

           As .csv is a text format all binary information is lost !
        """
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
        """
        writes the table in binary format. All information, as
        coresponding peakMaps are written too.

        The extension must be ".table".
        """
        if not os.path.splitext(path)[1].upper()==".TABLE":
            raise Exception("%s has wrong extension, need .table" % path)
        if not forceOverwrite and os.path.exists(path):
            raise Exception("%s exists. You may use forceOverwrite=True" % path)
        with open(path, "wb") as fp:
            cPickle.dump(self, fp)

    @staticmethod
    def load(path):
        """loads a table stored with Table.store"""
        with open(path, "rb") as fp:
            return cPickle.load(fp)


    def buildEmptyClone(self):
        return Table(self.colNames, self.colTypes, self.colFormats, [],
                     self.title, self.meta.copy())

    def dropColumn(self, name):
        """ removes a column with given *name* from the table.
            Works **inplace**
        """
        ix = self.getIndex(name)
        del self.colNames[ix]
        del self.colFormats[ix]
        del self.colTypes[ix]
        for row in self.rows:
            del row[ix]
        self.updateIndices()
        self.setupFormatters()
        self.emptyColumnCache()

    def addColumn(self, name, what, type_=None, format="", insertBefore=None):
        """
        adds a column **inplace**.

          - *name* is name of the new column, *type_* is one of the
            valid types described above.
          - format is a format string as "%d" or *None* or an executable
            string with python code.
            If you use *format=""* the method will try to determine a
            default format for the type.

        For the values *what* you can use

           - an expression as
           ``table.addColumn("diffrt", table.rtmax-table.rtmin)``
           - a callback with signature ``callback(table, row, name)``
           - a constant value

        If no value *what* is given, the column consists
        of *None* values.
        """
        assert isinstance(name, str) or isinstance(name, unicode),\
               "colum name is not a  string"

        if type_ is not None:
            assert isinstance(type_, type), "type_ param is not a type"

        if name in self.colNames:
            raise Exception("column with name %s already exists" % name)

        if isinstance(what, Node):
            return self._addColumnByExpression(name, what, type_, format,
                                               insertBefore)
        if callable(what):
            return self._addColumnByCallback(name, what, type_, format,
                                             insertBefore)

        if hasattr(what, "__iter__"):
            return self._addColumFromIterable(name, what, type_, format,
                                              insertBefore)

        return self.addConstantColumn(name, what, type_, format, insertBefore)

    def _addColumnByExpression(self, name, expr, type_, format, insertBefore):
        ctx = { self: self.getColumnCtx(expr.neededColumns()) }
        values, _ = expr.eval(ctx)
        return self._addColumn(name, values, type_, format, insertBefore)

    def _addColumnByCallback(self, name, callback, type_, format, insertBefore):
        values = [callback(self, r, name) for r in self.rows]
        return self._addColumn(name, values, type_, format, insertBefore)

    def _addColumFromIterable(self, name, iterable, type_, format, insertBefore):
        values = list(iterable)
        return self._addColumn(name, values, type_, format, insertBefore)

    def _addColumn(self, name, values, type_, format, insertBefore):
        if isinstance(values, np.ndarray):
            values = values.tolist()

        assert len(values) == len(self), "lenght of new column %d does not "\
                                         "fit number of rows %d in table"\
                                         % (len(values), len(self))
        if type_ is None:
            type_ = commonTypeOfColumn(values)
            conv = type_
        else:
            conv = lambda x: x
        if format == "":
            format = standardFormats.get(type_)

        if insertBefore is None:
            self.colNames.append(name)
            self.colTypes.append(type_)
            self.colFormats.append(format)
            for row, v in zip(self.rows, values):
                try:
                    row.append(type_(v))
                except:
                    row.append(v)  # type == object is not callable
        else:
            if isinstance(insertBefore, str):
                if insertBefore not in self.colNames:
                    raise Exception("column %s does not exist", insertBefore)
                insertBefore = self.getIndex(insertBefore)
                if insertBefore < 0: # incexing from back
                    insertBefore += len(self.colNames)
                self.colNames.insert(insertBefore, name)
                self.colTypes.insert(insertBefore, type_)
                self.colFormats.insert(insertBefore, format)
                for row, v in zip(self.rows, values):
                    row.insert(insertBefore, conv(v))

        self.setupFormatters()
        self.updateIndices()

    def addConstantColumn(self, name, value, type_=None, format="", insertBefore=None):
        """
        see addColumn 
        """
        return self._addColumn(name, [value]*len(self), type_, format,
                              insertBefore)

    def replaceColumn(self, name, expr, format=None):
        """as *Table.addColumn*, but replaces a given column. Eg::

                 table.replaceColumn("mzmin", table.mzmin*0.9)

           if the type of the column does not change, the format
           is kept unless *format* paramter is given.
           if the type changes and no format parameter is given,
           a standard format is used.

           one still can change the format afterwards by using
           ``Table.setFormat()``

        """
        #TODO: same semantics as addColumn !
        ix = self.getIndex(name)
        oldtype = self.colTypes[ix]
        ctx = { self: self.getColumnCtx(expr.neededColumns()) }
        values, _ = expr.eval(ctx)
        if isinstance(values, np.ndarray):
            values = values.tolist()
        t = commonTypeOfColumn(values)

        if t == oldtype and format is None:
            f = self.colFormats[ix]
        elif format is not None:
            f = format
        else:
            f= standardFormats.get(t)

        self.colNames[ix] = name
        self.colTypes[ix] = t
        self.colFormats[ix] = f
        for row, v in zip(self.rows, values):
            row[ix] = t(v)
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
        """builds a new table with columns selected according to *expr*. Eg ::

               table.filter(table.mz >= 100.0)
               table.filter((table.mz >= 100.0) & (table.rt <= 20))

        \\
        """
        assert isinstance(expr, Node)
        if debug:
            print "#", expr

        ctx = { self: self.getColumnCtx(expr.neededColumns()) }
        flags, _ = expr.eval(ctx)
        rv = self.buildEmptyClone()
        if flags is True:
            rv.rows = self.rows[:]
        elif flags is False:
            rv.rows = []
        else:
            rv.rows = [ self.rows[n] for n, i in enumerate(flags) if i ]
        return rv

    def join(self, t, expr, debug = False):
        """joins two tables.

           So if you have two table *t1* and *t2* as

           === ===
           id  mz
           === ===
           0   100.0
           1   200.0
           2   300.0
           === ===

           and

           ===    =====     ====
           id     mz        rt
           ===    =====     ====
           0      100.0     10.0
           1      110.0     20.0
           2      200.0     30.0
           ===    =====     ====
 
           Then the result of ``t1.join(t2, (t1.mz >= t2.mz -20) & (t1.mz <= t2.mz + 20)``
           is

           ====   =====  ====   =====  ====
           id_1   mz_1   id_2   mz_2   rt
           ====   =====  ====   =====  ====
           0      100.0  0      100.0  10.0
           0      100.0  1      110.0  20.0
           1      200.0  2      200.0  30.0
           ====   =====  ====   =====  ====

        """
        # no direct type check below, as databases decorate member tables:
        try:
            t.getColumnCtx
        except:
            raise Exception("first arg is of wrong type")
        assert isinstance(expr, Node)
        if debug:
            print "# %s.join(%s, %s)" % (self._name, t._name, expr)
        tctx = t.getColumnCtx(expr.neededColumns())

        cmdlineProgress = _CmdLineProgress(len(self))
        rows = []
        for ii, r1 in enumerate(self.rows):
            r1ctx = dict((n, (v, None)) for (n,v) in zip(self.colNames, r1))
            ctx = {self:r1ctx, t:tctx}
            flags,_ = expr.eval(ctx)
            if type(flags) == bool:
                if flags:
                    rows.extend([ r1 + row for row in t.rows])
            else:
                rows.extend([ r1 + t.rows[n] for (n,i) in enumerate(flags) if i])
            cmdlineProgress.progress(ii)
        print
        table = self._buildJoinTable(t)
        table.rows = rows
        return table

    def leftJoin(self, t, expr, debug = False, progress=True):
        """performs an *left join* also known as *outer join* of two tables.
           It works similar to *Table.join* but keeps nonmatching rows of
           the first table. So if we take the example from *Table.join*

           Then the result of ``t1.leftJoin(t2, (t1.mz >= t2.mz -20) & (t1.mz <= t2.mz + 20)``
           is

           ====   =====  ====   =====  ====
           id_1   mz_1   id_2   mz_2   rt
           ====   =====  ====   =====  ====
           0      100.0  0      100.0  10.0
           0      100.0  1      110.0  20.0
           1      200.0  2      200.0  30.0
           2      300.0  None   None   None
           ====   =====  ====   =====  ====

        """
        # no direct type check below, as databases decorate member tables:
        try:
            t.getColumnCtx
        except:
            raise Exception("first arg is of wrong type")
        assert isinstance(expr, Node)
        if debug:
            print "# %s.leftJoin(%s, %s)" % (self._name, t._name, expr)
        tctx = t.getColumnCtx(expr.neededColumns())

        filler = [None] * len(t.colNames)
        cmdlineProgress = _CmdLineProgress(len(self))

        rows = []
        for ii, r1 in enumerate(self.rows):
            r1ctx = dict((n, (v, None)) for (n,v) in zip(self.colNames, r1))
            ctx = {self:r1ctx, t:tctx}
            flags,_ = expr.eval(ctx)
            if flags is True:
                    rows.extend([ r1 + row for row in t.rows])
            elif flags is False:
                    rows.extend([ r1 + filler])
            elif numpy.any(flags):
                rows.extend([r1 + t.rows[n] for (n,i) in enumerate(flags) if i])
            else:
                rows.extend([r1 + filler])
            cmdlineProgress.progress(ii)
        print
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

    def _print(self, w=12, out=None):
        if out is None:
            out = sys.stdout
        #inner method is private, else the object can not be pickled !
        def _p(vals, w=w, out=out):
            expr = "%%-%ds" % w
            for v in vals:
                print >> out, (expr % v),

        _p(self.colNames)
        print >> out
        _p(re.match("<type '((\w|[.])+)'>|(\w+)", str(n)).groups()[0]  or str(n)
                                                   for n in self.colTypes)
        print >> out
        _p(["------"] * len(self.colNames))
        print >> out
        for row in self.rows:
            _p( fmt(value) for (fmt, value) in zip(self.colFormatters, row) )
            print >> out


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
