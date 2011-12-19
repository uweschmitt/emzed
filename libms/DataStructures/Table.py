import pyOpenMS as P
import copy, os, itertools, re, numpy, cPickle, sys, inspect
from   ExpressionTree import Node, Column
import numpy as np
from   collections import Counter, OrderedDict

standardFormats = { int: "%d", long: "%d", float : "%.2f", str: "%s" }
fms = "'%.2fm' % (o/60.0)"  # format seconds to floating point minutes

def guessFormatFor(name, type_):
    if type_ == float and name.startswith("m"):
        return  "%.5f"
    if type_ == float and name.startswith("rt"):
        return fms
    return standardFormats.get(name)

def computekey(o):
    if type(o) in [int, float, str, long]:
        return o
    if type(o) == dict:
        return computekey(o.items())
    if type(o) in [list, tuple]:
        return tuple(computekey(oi) for oi in o)
    print "HANDLE ", o
    return id(o)


class Bunch(dict):
    __getattr__ = dict.__getitem__

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

    differentTypes = set( type(c) for c in col )
    differentTypes.discard(type(None))

    hasStr = str in differentTypes
    hasInt = int in differentTypes
    hasLong = long in differentTypes
    hasFloat = float in differentTypes

    differentTypes.discard(str)
    differentTypes.discard(int)
    differentTypes.discard(long)
    differentTypes.discard(float)

    if len(differentTypes)==0:
        if hasStr:
            return str
        if hasFloat:
            return float
        if hasLong:
            return long
        if hasInt:
            return int
        return object
    if len(differentTypes) == 1:
        return differentTypes.pop()
    raise Exception("do not know how to find common type for types %r"\
                     % differentTypes)


def bestConvert(val):
    assert isinstance(val, str)
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
        def noneformat(s):
            return None
        return noneformat
    elif f.startswith("%"):
        def interpolationformat(s, f=f):
            try:
                return "-" if s is None else f % s
            except:
                print repr(s), repr(f)
                return ""
        return interpolationformat
    else:
        def evalformat(s, f=f):
            return "-" if s is None else eval(f, globals(), dict(o=s))
        return evalformat


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

        self.colTypes = list(colTypes)

        if any(type(t) in (np.float32, np.float64) for t in colTypes):
            print "WARNING: using numpy floats instead of python floats "\
                  "is not a good idea.\nTable operations may crash"

        self.colFormats = [None if f=="" else f for f in colFormats]

        self.rows = rows
        self.title = title
        self.meta = copy.copy(meta) if meta is not None else dict()

        self.primaryIndex = {}
        self._name = str(self)

        self.editableColumns = set()

        # as we provide  access to colums via __getattr__, colnames must
        # not be in objects __dict__ and must not be name of member
        # functions:
        memberNames = [name for name, obj in inspect.getmembers(self)]
        for name in colNames:
            if name in self.__dict__ or name in memberNames:
                raise Exception("colName %s not allowed" % name)

        self.resetInternals()

    def info(self):
        """
        prints some table information and some table statistics
        """
        import pprint
        print
        print "table info:"
        print
        print "   meta=",
        pprint.pprint(self.meta, indent=4)
        print "   len=", len(self)
        print
        for i, p in enumerate(zip(self.colNames, self.colTypes,\
                              self.colFormats)):
            vals = getattr(self, p[0]).values
            nones = sum( 1 for v in vals if v is None )
            numvals = len(set(id(v) for v in vals))
            txt = "[%d diff vals, %d Nones]" % (numvals, nones)
            print "   #%-2d %-25s name=%-8r %-15r fmt=%r"\
                  % ((i, txt)+p)
        print


    def addRow(self, row):
        """ adds a new row to the table, checks if values in row are of
            expected type or can be converted to this type """

        assert len(row) == len(self.colNames)
        # check for conversion !
        for i, (v, t) in enumerate(zip(row, self.colTypes)):
            if t!= object and v is not None:
                try:
                    row[i] = t(v)
                except:
                    raise Exception("value %r in col %d can not be converted "\
                                    "to type %s" % (v, i, t))
        self.rows.append(row)

    def isEditable(self, colName):
        return colName in self.editableColumns

    def _updateIndices(self):
        self.colIndizes = dict((n, i) for i, n in enumerate(self.colNames))

    def getVisibleCols(self):
        """ returns a list with the names of the columns which are
            visible. that is: the corresponding format is not None """
        return [n for (n, f) in zip (self.colNames, self.colFormats)\
                              if f is not None ]

    def getFormat(self, colName):
        """ returns for format for the given column *colName* """
        return self.colFormats[self.getIndex(colName)]

    def setFormat(self, colName, format):
        """ sets format of column *colName* to format *format* """
        self.colFormats[self.getIndex(colName)] = format
        self._setupFormatters()

    def setType(self, colName, type_):
        """ sets type of column *colName* to type *type_* """
        self.colTypes[self.getIndex(colName)] = type

    def _setupFormatters(self):
        self.colFormatters = [_formatter(f) for f in self.colFormats ]

    def getColumn(self, name):
        """ returns Column object for column *name*.
            to get the values of the colum you can use
            ``table.getColumn("index").values``
        """
        return getattr(self, name)

    def _setupColumnAttributes(self):
        for name in self.colNames:
            ix = self.getIndex(name)
            col = Column(self, name, ix)
            setattr(self, name, col)

    def __getstate__(self):
        """ for pickling. """
        dd = self.__dict__.copy()
        # self.colFormatters can not be pickled
        del dd["colFormatters"]
        for name in self.colNames:
            del dd[name]
        return dd

    def __setstate__(self, dd):
        self.__dict__ = dd
        self.resetInternals()

    def __iter__(self):
        """ returns iterator over rows """
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
        if type(value) in [np.float32, np.float64]:
            value = float(value)
        row[ix] = value
        self.resetInternals()

    def get(self, row, colName=None):
        """ returns value of column *colName* in a given *row*

            usage: ``table.get(table.rows[0], "mz")``

            if *colName* is not provided, one gets the content of
            the row as a dict mapping colnames to values.

            **Note**: you can use this for other lists according
            to columndata as

            ``table.get(table.colTypes)`` gives you a dict for
            getting a dict which maps colNames to the corresponding
            colTypes.

        """
        if colName is None:
            return Bunch( (n, self.get(row, n)) for n in self.colNames )
        return row[self.getIndex(colName)]

    def _getColumnCtx(self, needed):
        names = [ n for (t,n) in needed if t==self ]
        return dict((n, (self.getColumn(n).values,
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
        self.resetInternals()


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

        decorated = [ (row[idx], i) for (i, row) in enumerate(self.rows) ]
        decorated.sort(reverse=not ascending)
        permutation = [i for (_, i) in decorated]

        self.applyRowPermutation(permutation)

        if ascending:
            self.primaryIndex = {colName: True}
        else:
            self.primaryIndex = {}
        return permutation

    def applyRowPermutation(self, permutation):
        self.rows = [ self.rows[permutation[i]] for i in range(len(permutation))]
        self.resetInternals()

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
        for name in self.colNames:
            delattr(self, name)
        self.colNames = [ kw.get(n,n) for n in self.colNames]
        self.resetInternals()

    def __len__(self):
        return len(self.rows)

    def storeCSV(self, path, onlyVisibleColumns=True):
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
            if os.path.exists(p):
                print p, "exists"
            else:
                print "write ", p
                with file(p, "w") as fp:
                    if onlyVisibleColumns:
                        colNames = self.getVisibleCols()
                    else:
                        colNames = self.colNames
                    print >> fp, "; ".join(colNames)
                    for row in self.rows:
                        data = [self.get(row, v) for v in colNames]
                        print >> fp, "; ".join(map(str, data))
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
            tab = cPickle.load(fp)
            tab.meta["loaded_from"]=os.path.abspath(path)
            return tab


    def buildEmptyClone(self):
        """ returns empty table with same names, types, formatters,
            title and meta data """
        return Table(self.colNames, self.colTypes, self.colFormats, [],
                     self.title, self.meta.copy())

    def dropColumn(self, name):
        """ removes a column with given *name* from the table.
            Works **inplace**
        """
        self.requireColumn(name)
        delattr(self, name)
        ix = self.getIndex(name)
        del self.colNames[ix]
        del self.colFormats[ix]
        del self.colTypes[ix]
        for row in self.rows:
            del row[ix]
        self.resetInternals()

    def dropColumns(self, *names):
        """ removes columns with given *names* from the table.
            Works **inplace**
        """
        # check all names before maninuplating the table,
        # so this operation is atomic
        for name in names:
            self.requireColumn(name)
        for name in names:
            delattr(self, name)
            ix = self.getIndex(name)
            del self.colNames[ix]
            del self.colFormats[ix]
            del self.colTypes[ix]
            for row in self.rows:
                del row[ix]
        self.resetInternals()

    def splitBy(self, *colNames):
        """
        generates a list of subtables, where the columns given by *colNames*
        are unique.

        If we have a table ``t1`` as

        === === ===
        a   b   c
        === === ===
        1   1   1
        1   1   2
        2   1   3
        2   2   4
        === === ===

        ``res = t1.splitBy("a")`` results in a table ``res[0]`` as

        === === ===
        a   b   c
        === === ===
        1   1   1
        1   1   2
        === === ===

        ``res[1]`` which is like

        === === ===
        a   b   c
        === === ===
        2   1   3
        === === ===

        and ``res[2]`` which is

        === === ===
        a   b   c
        === === ===
        2   2   4
        === === ===


        """
        for name in colNames:
            self.requireColumn(name)

        groups = set()
        for row in self.rows:
            key = computekey([self.get(row, n) for n in colNames])
            groups.add(key)

        # preserve order of rows
        subTables = OrderedDict()
        for row in self.rows:
            key = computekey([self.get(row, n) for n in colNames])
            if key not in subTables:
                subTables[key] = self.buildEmptyClone()
            subTables[key].rows.append(row)
        splitedTables = subTables.values()
        for table in splitedTables:
            table.resetInternals()
        return splitedTables

    def append(self, *tables):
        """
        appends *tables* to the existing table **inplace**. Can be called as ::

              t1.append(t2, t3)
              t1.append([t2, t3])
              t1.append(t2, [t3, t4])

        the column names and the column types have to match !
        columnformat is taken from the original table.
        """
        alltables = []
        for table in tables:
            if type(table) == list:
                alltables.extend(table)
            elif isinstance(table, Table):
                alltables.append(table)
            else:
                raise Exception("can not join object %r" % table)

        names = set((tuple(t.colNames)) for t in alltables)
        if len(names)>1:
            raise Exception("the columNames do not match")

        types = set((tuple(t.colTypes)) for t in alltables)
        if len(types)>1:
            raise Exception("the columTypes do not match")
        for t in alltables:
            self.rows.extend(t.rows)
        self.resetInternals()

    def replaceColumn(self, name, what, type_=None, format=""):
        """
        replaces column *name* **inplace**.

          - *name* is name of the new column, *type_* is one of the
            valid types described above.
          - *format* is a format string as "%d" or *None* or an executable
            string with python code.
            If you use *format=""* the method will try to determine a
            default format for the type.

        For the values *what* you can use

           - an expression 
             as ``table.addColumn("diffrt", table.rtmax-table.rtmin)``
           - a callback with signature ``callback(table, row, name)``
           - a constant value

        If no value *what* is given, the column consists
        of *None* values.
        """

        self.requireColumn(name)
        # we do: 
        #      add tempcol, then delete oldcol, then rename tempcol -> oldcol
        # this is easier to implement, has no code duplication, but maybe a
        # bit slower. but that does not matter at this point of time:
        rv = self.addColumn(name+"__tmp", what, type_, format,\
                            insertBefore=name)
        self.dropColumn(name)
        self.renameColumns(**{name+"__tmp": name})
        return rv

    def addColumn(self, name, what, type_=None, format="", insertBefore=None):
        """
        adds a column **inplace**.

          - *name* is name of the new column, *type_* is one of the
            valid types described above.
          - *format* is a format string as "%d" or *None* or an executable
            string with python code.
            If you use *format=""* the method will try to determine a
            default format for the type.

        For the values *what* you can use

           - an expression 
             as ``table.addColumn("diffrt", table.rtmax-table.rtmin)``
           - a callback with signature ``callback(table, row, name)``
           - a constant value

        If you do not want the column be added at the end, one can use
        *insertBefore*, which maybe the name of an existing column, or an
        integer index (negative values allowed !).

        If no value *what* is given, the column consists of *None* values.

        """
        assert isinstance(name, str) or isinstance(name, unicode),\
               "colum name is not a  string"

        import types

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

        if type(what) in [list, tuple, types.GeneratorType, np.array]:
            return self._addColumFromIterable(name, what, type_, format,
                                              insertBefore)

        return self.addConstantColumn(name, what, type_, format, insertBefore)

    def _addColumnByExpression(self, name, expr, type_, format, insertBefore):
        ctx = { self: self._getColumnCtx(expr._neededColumns()) }
        values, _ = expr._eval(ctx)
        return self._addColumn(name, values, type_, format, insertBefore)

    def _addColumnByCallback(self, name, callback, type_, format, insertBefore):
        values = [callback(self, r, name) for r in self.rows]
        return self._addColumn(name, values, type_, format, insertBefore)

    def _addColumFromIterable(self, name, iterable, type_, format, insertBefore):
        values = list(iterable)
        return self._addColumn(name, values, type_, format, insertBefore)

    def _addColumn(self, name, values, type_, format, insertBefore):
        # works for lists, nubmers, objects: convers inner numpy dtypes
        # to python types if present, else does nothing !!!!
        if type(values) == np.ndarray:
            values = values.tolist()

        assert len(values) == len(self), "lenght of new column %d does not "\
                                         "fit number of rows %d in table"\
                                         % (len(values), len(self))
        if type_ is None:
            type_ = commonTypeOfColumn(values)
        def conv(x, type_=type_):
            if x is None:
                return x
            if type_ in [int, float, str, np.int32, np.int64, np.float32, np.float64]:
                return type_(x)
            return x
        if format == "":
            format = guessFormatFor(name, type_)

        if insertBefore is None:
            # list.insert(len(list), ..) is the same as append(..) !
            insertBefore = len(self.colNames)

        # colname -> index
        if isinstance(insertBefore, str):
            if insertBefore not in self.colNames:
                raise Exception("column %s does not exist", insertBefore)
            insertBefore = self.getIndex(insertBefore)

        # now insertBefore is an int, or something we can not handle
        if isinstance(insertBefore, int):
            if insertBefore < 0: # incexing from back
                insertBefore += len(self.colNames)
            self.colNames.insert(insertBefore, name)
            self.colTypes.insert(insertBefore, type_)
            self.colFormats.insert(insertBefore, format)
            for row, v in zip(self.rows, values):
                row.insert(insertBefore, conv(v))

        else:
            raise Exception("can not handle insertBefore=%r" % insertBefore)


        self.resetInternals()

    def addConstantColumn(self, name, value, type_=None, format="",\
                          insertBefore=None):
        """
        see addColumn
        """

        if type_ is not None:
            assert isinstance(type_, type), "type_ param is not a type"

        if name in self.colNames:
            raise Exception("column with name %s already exists" % name)

        return self._addColumn(name, [value]*len(self), type_, format,
                              insertBefore)


    def resetInternals(self):
        """ must be called after manipulation  of

            - self.colNames
            - self.colFormats

        or

            - self.rows
        """
        self._setupFormatters()
        self._updateIndices()
        self._setupColumnAttributes()

    def uniqueRows(self):
        """
        extracts table with unique rows.
        Two rows are equal if all fields, including **invisible**
        columns (those with format=None) are equal.
        """
        result = self.buildEmptyClone()
        keysSeen = set()
        for row in self.rows:
            key = computekey(row)
            if key not in keysSeen:
                result.rows.append(row)
                keysSeen.add(key)
        return result

    def aggregate(self, expr, newName, *groupByColumnNames):

        """
        adds new aggregated column to table **inplace**.
        *expr* calculates the aggregation.
        the table can be split into several subtables by
        providing extra *groupByColumnNames* parameters,
        then the aggregation is only performed per group.
        *newName* is the columnname for the aggregations.


        If we have a table ``t1`` with

           ===    =====     =====
           id     group     value
           ===    =====     =====
           0      1         10.0
           1      1         20.0
           2      2         30.0
           ===    =====     =====

       Then the result of ``t1.aggregate(t1.mean(), "mean_per_group", "group")``
       is

           ===    =====     =====  ==============
           id     group     value  mean_per_group
           ===    =====     =====  ==============
           0      1         10.0   15.0
           1      1         20.0   15.0
           2      2         30.0   30.0
           ===    =====     =====  ==============

        """
        subTables = self.splitBy(*groupByColumnNames)
        if len(subTables) == 0:
            rv = self.buildEmptyClone()
            rv.colNames.append(newName)
            rv.colTypes.append(object)
            rv.colFormats.append("%r")
            rv.resetInternals()
            return rv

        nc = expr._neededColumns()
        for t,_ in nc:
            if t!= self:
                raise Exception("illegal expression")
        names = [ n for (t,n) in nc ]
        collectedValues = []
        for t in subTables:
            ctx = dict((n, (t.getColumn(n).values,
                         t.primaryIndex.get(n))) for n in names)
            values, _ = expr._eval({self: ctx})
            # works for numbers and objects to, but not if values is
            # iteraable:
            if type(values) in [list, np.ndarray]:
                assert len(values)==1, "you did not use an aggregating "\
                                       "expression, or you aggregate over "\
                                       "a column which has lists or numpy "\
                                       "arrays as entries"
                values = np.array(values).tolist()
                values = values[0]
            collectedValues.extend([values]*len(t))

        self.addColumn(newName, collectedValues)


    def filter(self, expr, debug = False):
        """builds a new table with columns selected according to *expr*. Eg ::

               table.filter(table.mz >= 100.0)
               table.filter((table.mz >= 100.0) & (table.rt <= 20))

        \\
        """
        assert isinstance(expr, Node)
        if debug:
            print "#", expr

        ctx = { self: self._getColumnCtx(expr._neededColumns()) }
        flags, _ = expr._eval(ctx)
        filteredTable = self.buildEmptyClone()
        if flags is True:
            filteredTable.rows = self.rows[:]
        elif flags is False:
            filteredTable.rows = []
        else:
            filteredTable.rows = [ self.rows[n] for n, i in enumerate(flags) if i ]
        return filteredTable

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
            t._getColumnCtx
        except:
            raise Exception("first arg is of wrong type")
        assert isinstance(expr, Node)
        if debug:
            print "# %s.join(%s, %s)" % (self._name, t._name, expr)
        tctx = t._getColumnCtx(expr._neededColumns())

        cmdlineProgress = _CmdLineProgress(len(self))
        rows = []
        for ii, r1 in enumerate(self.rows):
            r1ctx = dict((n, (v, None)) for (n,v) in zip(self.colNames, r1))
            ctx = {self:r1ctx, t:tctx}
            flags,_ = expr._eval(ctx)
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
            t._getColumnCtx
        except:
            raise Exception("first arg is of wrong type")
        assert isinstance(expr, Node)
        if debug:
            print "# %s.leftJoin(%s, %s)" % (self._name, t._name, expr)
        tctx = t._getColumnCtx(expr._neededColumns())

        filler = [None] * len(t.colNames)
        cmdlineProgress = _CmdLineProgress(len(self))

        rows = []
        for ii, r1 in enumerate(self.rows):
            r1ctx = dict((n, (v, None)) for (n,v) in zip(self.colNames, r1))
            ctx = {self:r1ctx, t:tctx}
            flags,_ = expr._eval(ctx)
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
            colNames.append(name)
        for name in names2:
            if name in names1:
                name = name+"_1"
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

    @staticmethod
    def toTable(colName, iterable,  format=None, type_=None, title="", meta=None):
        """ generates a one-column table from an iterable, eg from a list,
            colName is name for the column.

            - if *type_* is not given a common type for all values is determined,
            - if *format* is not given, a default format for *type_* is used.

            further one can provide a title and meta data
        """
        if not isinstance(colName, str):
            raise Exception("colName is not a string. The arguments of this "\
                            "function changed in the past !")

        values = list(iterable)
        if type_ is None:
            type_ = commonTypeOfColumn(values)
        format = format or guessFormatFor(colName, type_) or "%r"
        if meta is None:
            meta = dict()
        else:
            meta = meta.copy()
        rows = [[v] for v in values]
        return Table([colName], [type_], [format], rows, title, meta)



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
