import pyOpenMS as P
import copy, os, itertools, re, numpy, cPickle, sys, inspect
from   ExpressionTree import Node, Column, Value
import numpy as np
from   collections import Counter, OrderedDict, defaultdict

standardFormats = { int: "%d", long: "%d", float : "%.2f", str: "%s" }
fms = "'%.2fm' % (o/60.0)"  # format seconds to floating point minutes

def guessFormatFor(name, type_):
    if type_ == float and name.startswith("m"):
        return  "%.5f"
    if type_ == float and name.startswith("rt"):
        return fms
    return standardFormats.get(type_)

def computekey(o):
    if type(o) in [int, float, str, long]:
        return o
    if type(o) == dict:
        return computekey(o.items())
    if type(o) in [list, tuple]:
        return tuple(computekey(oi) for oi in o)
    print "HANDLE ", o
    return id(o)


def getPostfix(colName):
    if colName.startswith("__"): # internal colnames may start with __
        colName = colName[2:]
    fields = colName.split("__")
    if len(fields)>2:
        raise Exception("invalid colName %s" % colName)
    if len(fields) == 1:
        return ""
    try:
        return "__"+fields[1]
    except:
        raise Exception("invalid postfix '%s'" % fields[1])


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
                       meta=None, circumventNameCheck=False):

        if len(colNames) != len(set(colNames)):
            counts = Counter(colNames)
            multiples = [name for (name, count) in counts.items() if count>1]
            message = "multiple columns: " + ", ".join(multiples)
            raise Exception(message)

        if not circumventNameCheck:
            assert all("__" not in name  for name in colNames), \
                       "illegal column name(s), double underscores not allowed"

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
                raise Exception("colName '%s' not allowed" % name)

        self.resetInternals()

    def info(self):
        """
        prints some table information and some table statistics
        """
        import pprint
        print
        print "table info:   title=", self.title
        print
        print "   meta=",
        pprint.pprint(self.meta)
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


    def addRow(self, row, doResetInternals=True):
        """ adds a new row to the table, checks if values in row are of
            expected type or can be converted to this type """

        assert len(row) == len(self.colNames)
        # check for conversion !
        for i, (v, t) in enumerate(zip(row, self.colTypes)):
            if v is not None and t in [int, float, long, str]:
                    row[i] = t(v)
            else:
                row[i] = v
        self.rows.append(row)
        if doResetInternals:
            self.resetInternals()


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

    def numRows(self):
        return len(self.rows)

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
            raise Exception("colname %r not in table" % colName)
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

    def addEnumeration(self, colName="id"):
        """ adds enumerated column as first column to table **inplace**.

            if *colName* is not given the colName is "id"

            Enumeration starts with zero
        """

        if colName in self.colNames:
            raise Exception("column with name %r already exists" % colName)
        self.colNames.insert(0, colName)
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
        assert len(set(names)) == len(names), "duplicate column name"
        indices = [self.getIndex(name)  for name in names]
        types = [ self.colTypes[i] for i in indices ]
        formats = [self.colFormats[i] for i in indices]
        rows = [[row[i] for i in indices] for row in self.rows]
        return Table(names, types, formats, rows, self.title,
                     self.meta.copy(), circumventNameCheck=True)

    def renameColumns(self, **kw):
        """renames colums **inplace**.
           So if you want to rename "mz_1" to "mz" and "rt_1"
           to "rt", ``table.renameColumns(mz_1=mz, rt_1=rt)``
        """

        newNames = set(kw.values())
        if len(newNames)<len(kw):
            raise Exception("you try to rename two columns to the same name")
        for name in newNames:
            if name in self.colNames:
                raise Exception("column %s allready exists" % name)

        for k in kw.keys():
            if k not in self.colNames:
                raise Exception("colum %r does not exist" % k)

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
        with open(path, "w+b") as fp:
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
                     self.title, self.meta.copy(), circumventNameCheck=True)

    def dropColumn(self, name):
        """ removes a column with given *name* from the table.
            Works **inplace**
        """
        return self.dropColumns(name)

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

        indices = [ self.getIndex(n) for n in names ]
        indices.sort()
        for ix in reversed(indices):
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
            subTables[key].rows.append(row[:])
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

    def updateColumn(self, name, what, type_=None, format="",
                         insertBefore=None):
        if self.hasColumn(name):
            self.dropColumn(name)

        return self.addColumn(name, what, type_, format, insertBefore)

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
            raise Exception("column with name %r already exists" % name)

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
        values, _ = expr._eval(None)
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
                raise Exception("column %r does not exist", insertBefore)
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
            raise Exception("column with name '%s' already exists" % name)

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
                result.rows.append(row[:])
                keysSeen.add(key)
        return result

    def aggregate(self, expr, newName, groupBy=None):

        """
        adds new aggregated column to table **inplace**.
        *expr* calculates the aggregation.
        the table can be split into several subtables by
        providing an extra *groupBy* parameter,
        which can be a colummname or a list of columnames,
        then the aggregation is only performed per group.

        In each group the values corresponding to *groupBy*
        are constant.

        *newName* is the columnname for the aggregations.

        If we have a table ``t1`` with

           ===    ======    =====
           id     source    value
           ===    ======    =====
           0      1         10.0
           1      1         20.0
           2      2         30.0
           ===    ======    =====

        Then the result of

        ``t1.aggregate(t1.value.mean, "mean_per_source", groupBy="source")``

        is

           ===    ======    =====  ===============
           id     source    value  mean_per_source
           ===    ======    =====  ===============
           0      1         10.0   15.0
           1      1         20.0   15.0
           2      2         30.0   30.0
           ===    ======    =====  ===============

        Here we got two different row groups, in each group the value of *source*
        is constant. So we have one group:

           ===    ======    =====
           id     source    value
           ===    ======    =====
           0      1         10.0
           1      1         20.0
           ===    ======    =====

        and second one which is:

           ===    ======    =====
           id     source    value
           ===    ======    =====
           2      2         30.0
           ===    ======    =====

        Without grouping
        the full table is one row group and the statement

        ``t1.aggregate(t1.value.mean, "mean_per_source")``

        results in:

           ===    ======    =====  ===============
           id     source    value  mean_per_source
           ===    ======    =====  ===============
           0      1         10.0   20.0
           1      1         20.0   20.0
           2      2         30.0   20.0
           ===    ======    =====  ===============


        And if we group by identical (id, source) pairs, each row is in separate
        group and so

        ``t1.aggregate(t1.value.mean, "mean_per_source", groupBy=["id", "source"])``

        delivers:

           ===    ======    =====  ===============
           id     source    value  mean_per_source
           ===    ======    =====  ===============
           0      1         10.0   10.0
           1      1         20.0   20.0
           2      2         30.0   30.0
           ===    ======    =====  ===============

        """
        if isinstance(groupBy, str):
            groupBy = [groupBy]
        elif groupBy is None:
            groupBy = []

        subTables = self.splitBy(*groupBy)
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
            if type(values) in (list, np.ndarray):
                assert len(values)==1, "you did not use an aggregating "\
                                       "expression, or you aggregate over "\
                                       "a column which has lists or numpy "\
                                       "arrays as entries"
                values = np.array(values).tolist()
                values = values[0]
            else:
                if hasattr(values, "__array_interface__"):
                    values = values.tolist()
            collectedValues.extend([values]*len(t))

        result = self.copy()
        result.addColumn(newName, collectedValues)
        return result

    def filter(self, expr, debug = False):
        """builds a new table with columns selected according to *expr*. Eg ::

               table.filter(table.mz >= 100.0)
               table.filter((table.mz >= 100.0) & (table.rt <= 20))

        \\
        """
        if not isinstance(expr, Node):
            expr = Value(expr)

        if debug:
            print "#", expr

        flags, _ = expr._eval(None)
        filteredTable = self.buildEmptyClone()
        if flags is True:
            filteredTable.rows = [r[:] for r in  self.rows]
        elif flags is False:
            filteredTable.rows = []
        else:
            assert len(flags) == len(self),\
                   "result of filter expression does not match table size"
            filteredTable.rows =\
                    [self.rows[n][:] for n, i in enumerate(flags) if i]
        return filteredTable

    def supportedPostfixes(self, colNamesToSupport):

        collected = defaultdict(list)
        for name in self.colNames:
            for prefix in colNamesToSupport:
                if name.startswith(prefix):
                    collected[prefix].append(name[len(prefix):])

        counter = defaultdict(int)
        for postfixes in collected.values():
            for postfix in postfixes:
                counter[postfix] += 1

        supported = [ pf for pf, count in counter.items()
                                       if count == len(colNamesToSupport)]

        return sorted(set(supported))

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

        if not isinstance(expr, Node):
            expr = Value(expr)

        table = self._buildJoinTable(t)

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
                    rows.extend([ r1[:] + row[:] for row in t.rows])
            else:
                rows.extend([ r1[:] + t.rows[n][:] for (n,i) in enumerate(flags) if i])
            cmdlineProgress.progress(ii)
        print
        table.rows = rows
        return table

    def leftJoin(self, t, expr, debug = False, progress=False):
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

        if not isinstance(expr, Node):
            expr = Value(expr)

        table = self._buildJoinTable(t)

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
                rows.extend([ r1[:] + row[:] for row in t.rows])
            elif flags is False:
                rows.extend([ r1[:] + filler[:]])
            elif numpy.any(flags):
                rows.extend([r1[:] + t.rows[n][:] for (n,i) in enumerate(flags) if i])
            else:
                rows.extend([r1[:] + filler[:]])
        if progress:
            cmdlineProgress.progress(ii)

        table.rows = rows
        return table

    def maxPostfix(self):
        """ finds postfixes 1, 2, .. in  __1, __2, ... in self.colNames
            an empty postfix "" is recognized as __0 """
        postfixes = set( getPostfix(c) for c in self.colNames )
        values = [ -1 if p=="" else int(p[2:]) for p in postfixes ]
        return  max(values)

    def findPostfixes(self):
        return sorted(set( getPostfix(c) for c in self.colNames) )

    def incrementedPostfixes(self, by):
        newColNames = []
        for c in self.colNames:
            pf = getPostfix(c)
            val = 0 if pf =="" else int(pf[2:])
            prefix = c if pf == "" else c[:-2]
            newName = prefix+"__"+str(by+val)
            newColNames.append(newName)
        return newColNames

    def _buildJoinTable(self, t):

        incrementBy = self.maxPostfix()+1

        colNames = self.colNames + list(t.incrementedPostfixes(incrementBy))

        colFormats = self.colFormats + t.colFormats
        colTypes = self.colTypes + t.colTypes
        title = "%s vs %s" % (self.title, t.title)
        meta = {self: self.meta.copy(), t: t.meta.copy()}
        return Table(colNames, colTypes, colFormats, [], title, meta,
                     circumventNameCheck=True)

    def _print(self, w=12, out=None, title=None):
        if out is None:
            out = sys.stdout
        #inner method is private, else the object can not be pickled !
        def _p(vals, w=w, out=out):
            expr = "%%-%ds" % w
            for v in vals:
                v = "-" if v is None else v
                print >> out, (expr % v),

        if title is not None:
            _p(["==============="])
            print >> out
            _p([title])
            print >> out
            _p(["==============="])
            print >> out

        ix = [ i for i, f in enumerate(self.colFormats) if f is not None ]

        _p([self.colNames[i] for i in ix])
        print >> out
        ct = [ self.colTypes[i] for i in ix]

        _p(re.match("<(type|class) '((\w|[.])+)'>|(\w+)", str(n)).groups()[1]  or str(n)
                                                   for n in ct)
        print >> out
        _p(["------"] * len(ix))
        print >> out
        fms = [ self.colFormatters[i] for i in ix]
        for row in self.rows:
            ri = [ row[i] for i in ix]
            _p( fmt(value) for (fmt, value) in zip(fms, ri))
            print >> out

    print_ = _print

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
        return Table([colName], [type_], [format], rows, meta=meta)

def toOpenMSFeatureMap(table):
    table.requireColumn("mz")
    table.requireColumn("rt")

    if "into" in table.colNames:
        areas = table.into.values
    elif "area" in table.colNames:
        areas = table.area.values
    else:
        print "features not integrated. I assume const intensity"
        areas = [None] * len(table)


    mzs = table.mz.values
    rts = table.rt.values
    fm = P.FeatureMap()

    for (mz, rt, area) in zip(mzs, rts, areas):
        f = P.Feature()
        f.setMZ(mz)
        f.setRT(rt)
        f.setIntensity(area if area is not None else 1000.0)
        fm.push_back(f)
    return fm
