import pyOpenMS as P
import copy, os, itertools, re, numpy, cPickle, sys, inspect
from   Expressions import BaseExpression, ColumnExpression, Value, _basic_num_types, common_type_for
import numpy as np
from   collections import Counter, OrderedDict, defaultdict


__doc__ = """

"""


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
        return computekey(sorted(o.items()))
    if type(o) in [list, tuple]:
        return tuple(computekey(oi) for oi in o)
    return id(o)


def getPostfix(colName):
    if colName.startswith("__"):
        return None

    fields = colName.split("__")

    if len(fields)>2:
        raise Exception("invalid colName %s" % colName)
    if len(fields) == 1:
        return ""
    return "__"+fields[1]

def convert_list_to_overall_type(li):
    ct = common_type_for(li)
    if ct is not object:
        return  [ None if x is None else ct(x) for x in li]
    return li


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
    """ helper, is top level for supporting pickling of Table """

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
    A table holds rows of the same length. Each Column of the table has
    a *name*, a *type* and *format* information, which indicates how to render
    values in this column.
    Further a table has a title and meta information which is a dictionary.

    column types can be any python type.

    format can be:

         - a string interpolation string, e.g. "%.2f"
         - ``None``, which suppresses rendering of this column
         - python code which renders an object of name ``o``, e.g.
           ``str(o)+"x"``

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

        if not all(isinstance(row, list) for row in rows):
            raise Exception("not all rows are lists !")

        self.colNames = list(colNames)

        self.colTypes = list(colTypes)

        is_numpy_type = lambda t: np.number in t.__mro__

        if any(is_numpy_type(t) for t in colTypes):
            raise Exception("using numpy floats instead of python floats "\
                  "is not a good idea.\nTable operations may crash")

        self.colFormats = [None if f=="" else f for f in colFormats]

        self.rows = rows
        self.title = title
        self.meta = copy.copy(meta) if meta is not None else dict()

        self.primaryIndex = {}
        self._name = str(self)

        self.editableColumns = set()

        # as we provide  access to columns via __getattr__, colNames must
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
        print "   rows=", len(self)
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
            expected type or can be converted to this type.

            Raises an ``AssertException`` if the length of ``row`` does not
            match to the numbers of columns of the table.
            """

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
        """ returns for format for the given column ``colName`` """
        return self.colFormats[self.getIndex(colName)]

    def getType(self, colName):
        """ returns for format for the given column ``colName`` """
        return self.colTypes[self.getIndex(colName)]

    def _setupFormatters(self):
        self.colFormatters = [_formatter(f) for f in self.colFormats ]

    def getColumn(self, name):
        """ returns ColumnExpression object for column ``name``.
            to get the values of the column you can use
            ``table.getColumn("index").values``.

            See: :py:class:`~libms.DataStructures.Expressions.ColumnExpression`
        """
        return getattr(self, name)

    def _setupColumnAttributes(self):
        for name in self.colNames:
            ix = self.getIndex(name)
            col = ColumnExpression(self, name, ix, self.colTypes[ix])
            setattr(self, name, col)

    def numRows(self):
        """
        returns the number of rows
        """
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
        """ checks if column with given name ``name`` exists """
        return name in self.colNames

    def hasColumns(self, *names):
        """ checks if columns with given names exist.

            Example: ``tab.hasColumn("rt", "rtmin", "rtmax")``
        """
        return all(self.hasColumn(n) for n in names)

    def requireColumn(self, name):
        """ throws exception if column with name ``name`` does not exist"""
        if not name in self.colNames:
            raise Exception("column %r required" % name)
        return self

    def getIndex(self, colName):
        """ gets the integer index of the column ``colName``.

            Example: ``table.rows[0][table.getIndex("mz")]``
            """
        idx = self.colIndizes.get(colName, None)
        if idx is None:
            raise Exception("column with name %r not in table" % colName)
        return idx

    def set(self, row, colName, value):
        """ sets ``value`` of column ``colName`` in a given ``row``.

            Example: ``table.set(table.rows[0], "mz", 252.83332)``
        """
        ix = self.getIndex(colName)
        if type(value) in [np.float32, np.float64]:
            value = float(value)
        row[ix] = value
        self.resetInternals()

    def get(self, row, colName=None):
        """ returns value of column ``colName`` in a given ``row``

            Example: ``table.get(table.rows[0], "mz")``

            if ``colName`` is not provided, one gets the content of
            the ``row`` as a dictionary mapping column names to values.

            Example::

                row = table.get(table.rows[0])
                print row["mz"]

            **Note**: you can use this for other lists according
            to column data as

            ``table.get(table.colTypes)`` gives you a dictionary for
            which maps column names to the corresponding column types.

            Example::

                types = table.get(table.colTypes)
                print types["mz"]

                formats = table.get(table.colFormats)
                print formats["mz"]

        """
        if colName is None:
            return Bunch( (n, self.get(row, n)) for n in self.colNames )
        return row[self.getIndex(colName)]

    def _getColumnCtx(self, needed):
        names = [ n for (t,n) in needed if t==self ]
        return dict((n, (self.getColumn(n).values,
                         self.primaryIndex.get(n),
                         self.getColumn(n).type_)) for n in names)

    def addEnumeration(self, colName="id"):
        """ adds enumerated column as first column to table **in place**.

            if ``colName`` is not given the default name is *"id"*

            Enumeration starts with zero.
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
        sorts table in respect of column named *colName* **in place**.
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

        self._applyRowPermutation(permutation)

        if ascending:
            self.primaryIndex = {colName: True}
        else:
            self.primaryIndex = {}
        return permutation

    def _applyRowPermutation(self, permutation):
        self.rows = [ self.rows[permutation[i]] for i in range(len(permutation))]
        self.resetInternals()

    def copy(self):
        """ returns a 'semi-deep' copy of the table """
        prototype = self.buildEmptyClone()
        for row in self.rows:
            prototype.rows.append(row[:])
        prototype.resetInternals()
        return prototype

    def extractColumns(self, *names):
        """extracts the given column names ``names`` and returns a new
           table with these columns

           Example: ``t.extractColumns("id", "name"))``
           """
        assert len(set(names)) == len(names), "duplicate column name"
        indices = [self.getIndex(name)  for name in names]
        types = [ self.colTypes[i] for i in indices ]
        formats = [self.colFormats[i] for i in indices]
        rows = [[row[i] for i in indices] for row in self.rows]
        return Table(names, types, formats, rows, self.title,
                     self.meta.copy(), circumventNameCheck=True)

    def renameColumns(self, **kw):
        """renames columns **in place**.

           So if you want to rename "mz_1" to "mz" and "rt_1"
           to "rt", ``table.renameColumns(mz_1=mz, rt_1=rt)``

           For memorization read the ``=`` as ``->``.
        """

        newNames = set(kw.values())
        if len(newNames)<len(kw):
            raise Exception("you try to rename two columns to the same name")
        for name in newNames:
            if name in self.colNames:
                raise Exception("column %s already exists" % name)

        for k in kw.keys():
            if k not in self.colNames:
                raise Exception("column %r does not exist" % k)

        for name in self.colNames:
            delattr(self, name)
        self.colNames = [ kw.get(n,n) for n in self.colNames]
        self.resetInternals()

    def __len__(self):
        return len(self.rows)

    def storeCSV(self, path, onlyVisibleColumns=True):
        """writes the table in .csv format. The ``path`` has to end with
           '.csv'.

           If the file already exists, the routine tries names
           ``*.csv.1, *.csv.2, ...`` until a non-existing file name is found

           As .csv is a text format all binary information is lost !
        """
        if not os.path.splitext(path)[1].upper()==".CSV":
            raise Exception("%s has wrong file type extension" % path)
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
        corresponding peak maps are written too.
        The file name extension must be ".table".

        Latter the file can be loaded with :py:meth:`~.load`
        """
        if not forceOverwrite and os.path.exists(path):
            raise Exception("%s exists. You may use forceOverwrite=True" % path)
        with open(path, "w+b") as fp:
            cPickle.dump(self, fp, protocol=2)

    @staticmethod
    def load(path):
        """loads a table stored with :py:meth:`~.store`

           **Note**: as this is a static method, it has to be called as
           ``tab = Table.load("xzy.table")``

        """
        with open(path, "rb") as fp:
            tab = cPickle.load(fp)
            tab.meta["loaded_from"]=os.path.abspath(path)
            return tab


    def buildEmptyClone(self):
        """ returns empty table with same names, types, formatters,
            title and meta data """
        return Table(self.colNames, self.colTypes, self.colFormats, [],
                     self.title, self.meta.copy(), circumventNameCheck=True)

    def dropColumns(self, *names):
        """ removes columns with given ``names`` from the table.
            Works **in place**

            Example: ``tab.dropColumns("mz", "rt", "rmse")``
        """
        # check all names before manipulating the table,
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
        generates a list of subtables, where the columns given by ``colNames``
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
        appends ``tables`` to the existing table **in place**. Can be called as ::

              t1.append(t2, t3)
              t1.append([t2, t3])
              t1.append(t2, [t3, t4])

        the column names and the column types have to match !
        column format is taken from the original table.
        """
        alltables = []
        for table in tables:
            if type(table) in [list, tuple]:
                alltables.extend(table)
            elif isinstance(table, Table):
                alltables.append(table)
            else:
                raise Exception("can not join object %r" % table)

        names = set((tuple(t.colNames)) for t in alltables)
        if len(names)>1:
            raise Exception("the column names do not match")

        types = set((tuple(t.colTypes)) for t in alltables)
        if len(types)>1:
            raise Exception("the column types do not match")
        for t in alltables:
            self.rows.extend(t.rows)
        self.resetInternals()

    def replaceColumn(self, name, what, type_=None, format=""):
        """
        replaces column ``name`` **in place**.

          - ``name`` is name of the new column
          - ``*type_`` is one of the valid types described above.
            If ``type_ == None`` the method tries to guess the type from ``what``.
          - ``format`` is a format string as "%d" or ``None`` or an executable
            string with python code.
            If you use ``format=""`` the method will try to determine a
            default format for the type.

        For the values ``what`` you can use

           - an expression (see :py:class:`~libms.DataStructures.Expressions`)
             as ``table.addColumn("diffrt", table.rtmax-table.rtmin)``
           - a callback with signature ``callback(table, row, name)``
           - a constant value
           - a list with the correct length.

        """

        self.requireColumn(name)
        # we do:
        #      add tempcol, then delete oldcol, then rename tempcol -> oldcol
        # this is easier to implement, has no code duplication, but maybe a
        # bit slower. but that does not matter at this point of time:
        rv = self.addColumn(name+"__tmp", what, type_, format,\
                            insertBefore=name)
        self.dropColumns(name)
        self.renameColumns(**{name+"__tmp": name})
        return rv

    def updateColumn(self, name, what, type_=None, format="",
                         insertBefore=None):
        """
        Replaces the column ``name`` if it exists. Else the column is added.

        For the parameters see :py:meth:`~.addColumn`
        """
        if self.hasColumn(name):
            self.dropColumns(name)

        return self.addColumn(name, what, type_, format, insertBefore)

    def addColumn(self, name, what, type_=None, format="", insertBefore=None):
        """
        adds a column **in place**.

        For the meaning of the  parameters
        see :py:meth:`~.replaceColumn`

        If you do not want the column be added at the end, one can use
        ``insertBefore``, which maybe the name of an existing column, or an
        integer index (negative values allowed !).

        """
        assert isinstance(name, str) or isinstance(name, unicode),\
               "colum name is not a  string"

        import types

        if type_ is not None:
            assert isinstance(type_, type), "type_ param is not a type"

        if name in self.colNames:
            raise Exception("column with name %r already exists" % name)

        if isinstance(what, BaseExpression):
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
        values, _, type2_ = expr._eval(None)
        return self._addColumn(name, values, type_ or type2_, format, insertBefore)

    def _addColumnByCallback(self, name, callback, type_, format, insertBefore):
        values = [callback(self, r, name) for r in self.rows]
        return self._addColumn(name, values, type_, format, insertBefore)

    def _addColumFromIterable(self, name, iterable, type_, format, insertBefore):
        values = list(iterable)
        return self._addColumn(name, values, type_, format, insertBefore)

    def _addColumn(self, name, values, type_, format, insertBefore):
        # works for lists, numbers, objects: converts inner numpy dtypes
        # to python types if present, else does nothing !!!!

        assert len(values) == len(self), "length of new column %d does not "\
                                         "fit number of rows %d in table"\
                                         % (len(values), len(self))

        if type(values) == np.ma.core.MaskedArray:
            values = values.tolist() # handles missing values as None !

        # type_ may be None, so guess:
        type_ = type_ or  common_type_for(values)

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
            if insertBefore < 0: # indexing from back
                insertBefore += len(self.colNames)
            self.colNames.insert(insertBefore, name)
            self.colTypes.insert(insertBefore, type_)
            self.colFormats.insert(insertBefore, format)
            for row, v in zip(self.rows, values):
                row.insert(insertBefore, v)

        else:
            raise Exception("can not handle insertBefore=%r" % insertBefore)


        self.resetInternals()

    def addConstantColumn(self, name, value, type_=None, format="",\
                          insertBefore=None):
        """
        see :py:meth:`~.addColumn`.

        ``value`` is inserted in the column, despite its class. So the
        cases in py:meth:`~.addColumn` are not considered, which is useful,
        e.g. if you want to set all cells in a column to as ``list``.
        """

        if type_ is not None:
            assert isinstance(type_, type), "type_ param is not a type"

        if name in self.colNames:
            raise Exception("column with name '%s' already exists" % name)

        return self._addColumn(name, [value]*len(self), type_, format,
                              insertBefore)


    def resetInternals(self):
        """  **internal method**

            must be called after manipulation  of

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
        columns (those with ``format==None``) are equal.
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
        adds new aggregated column to table **in place**.

        ``expr`` calculates the aggregation.

        The table can be split into several subtables by
        providing an extra ``groupBy`` parameter,
        which can be a column name or a list of column names,
        then the aggregation is only performed per group.

        In each group the values corresponding to ``groupBy``
        are constant.

        ``newName`` is the column name for the aggregations.

        If we have a table ``t1`` with

           ===    ======    =====
           id     source    value
           ===    ======    =====
           0      1         10.0
           1      1         20.0
           2      2         30.0
           ===    ======    =====

        Then the result of

        ``t1.aggregate(t1.value.mean, "mean")``

        is

           ===    ======    =====  ====
           id     source    value  mean
           ===    ======    =====  ====
           0      1         10.0   20.0
           1      1         20.0   20.0
           2      2         30.0   20.0
           ===    ======    =====  ====

        If you group by column ``source``, for example as

        ``t1.aggregate(t1.value.mean, "mean_per_source", groupBy="source")``

        the result is

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

        if len(self) == 0:
            rv = self.buildEmptyClone()
            rv.colNames.append(newName)
            rv.colTypes.append(object)
            rv.colFormats.append("%r")
            rv.resetInternals()
            return rv

        subTables = self.splitBy(*groupBy)
        nc = expr._neededColumns()
        for t,_ in nc:
            if t!= self:
                raise Exception("illegal expression")
        names = [ n for (t,n) in nc ]
        collectedValues = []
        for t in subTables:
            print
            print "subt"
            t._print()
            ctx = dict((n, (t.getColumn(n).values,
                         t.primaryIndex.get(n),
                         t.getColumn(n).type_
                         )) for n in names)
            value, _, type_ = expr._eval({self: ctx})
            # works for numbers and objects to, but not if values is
            # iterable:
            assert len(value)==1, "you did not use an aggregating "\
                                   "expression, or you aggregate over "\
                                   "a column which has lists or numpy "\
                                   "arrays as entries"

            print repr(value), type_
            if type_ in _basic_num_types:
                value = value.tolist()
            collectedValues.extend(value*len(t))

        result = self.copy()
        result.addColumn(newName, collectedValues)
        result.primaryIndex = self.primaryIndex.copy()
        return result

    def filter(self, expr, debug = False):
        """builds a new table with columns selected according to ``expr``. E.g. ::

               table.filter(table.mz >= 100.0)
               table.filter((table.mz >= 100.0) & (table.rt <= 20))

        \\
        """
        if not isinstance(expr, BaseExpression):
            expr = Value(expr)

        if debug:
            print "#", expr

        ctx = {self: self._getColumnCtx(expr._neededColumns())}
        flags, _, _ = expr._eval(ctx)
        filteredTable = self.buildEmptyClone()
        filteredTable.primaryIndex = self.primaryIndex.copy()
        if len(flags) == 1:
            if flags[0]:
                filteredTable.rows = [r[:] for r in  self.rows]
            else:
                filteredTable.rows = []
        else:
            assert len(flags) == len(self),\
                   "result of filter expression does not match table size"
            filteredTable.rows =\
                    [self.rows[n][:] for n, i in enumerate(flags) if i]
        return filteredTable

    def supportedPostfixes(self, colNamesToSupport):
        """

        For a table with column names ``["rt", "rtmin", "rtmax", "rt1", "rtmin1"]``

        ``supportedPostfixes(["rt"])`` returns ``["", "min", "max", "1", "min1"]``,

        ``supportedPostfixes(["rt", "rtmin"])`` returns ``["", "1"]``,

        ``supportedPostfixes(["rt", "rtmax"])`` returns ``[""]``,

        """

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

    def join(self, t, expr=True, debug=False):
        """joins two tables.

           So if you have two table ``t1`` and ``t2`` as

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

           If you do not provide an expression, this method returns the full
           cross product.

        """
        # no direct type check below, as databases decorate member tables:
        try:
            t._getColumnCtx
        except:
            raise Exception("first arg is of wrong type")

        if not isinstance(expr, BaseExpression):
            expr = Value(expr)

        table = self._buildJoinTable(t)

        if debug:
            print "# %s.join(%s, %s)" % (self._name, t._name, expr)
        tctx = t._getColumnCtx(expr._neededColumns())

        cmdlineProgress = _CmdLineProgress(len(self))
        rows = []
        for ii, r1 in enumerate(self.rows):
            r1ctx = dict((n, ([v], None, t)) for (n,v, t) in zip(self.colNames, r1, self.colTypes))
            ctx = {self:r1ctx, t:tctx}
            flags,_,_ = expr._eval(ctx)
            if len(flags) == 1:
                if flags[0]:
                    rows.extend([ r1[:] + row[:] for row in t.rows])
            else:
                rows.extend([ r1[:] + t.rows[n][:] for (n,i) in enumerate(flags) if i])
            cmdlineProgress.progress(ii)
        print
        table.rows = rows
        return table

    def leftJoin(self, t, expr=True, debug=False, progress=False):
        """performs an *left join* also known as *outer join* of two tables.

           It works similar to :py:meth:`~.join`
           but keeps non-matching rows of
           the first table. So if we take the example from
           :py:meth:`~.join`

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

           If you do not provide an expression, this method returns the full
           cross product.
        """
        # no direct type check below, as databases decorate member tables:
        try:
            t._getColumnCtx
        except:
            raise Exception("first argument is of wrong type")

        if not isinstance(expr, BaseExpression):
            expr = Value(expr)

        table = self._buildJoinTable(t)

        if debug:
            print "# %s.leftJoin(%s, %s)" % (self._name, t._name, expr)
        tctx = t._getColumnCtx(expr._neededColumns())

        filler = [None] * len(t.colNames)
        cmdlineProgress = _CmdLineProgress(len(self))

        rows = []
        for ii, r1 in enumerate(self.rows):
            r1ctx = dict((n, ([v], None, t)) for (n,v, t) in zip(self.colNames, r1, self.colTypes))
            ctx = {self:r1ctx, t:tctx}
            flags,_,_ = expr._eval(ctx)
            if len(flags) == 1:
                if flags[0]:
                    rows.extend([ r1[:] + row[:] for row in t.rows])
                else:
                    rows.extend([ r1[:] + filler[:]])
            elif numpy.any(flags):
                rows.extend([r1[:] + t.rows[n][:] for (n,i) in enumerate(flags) if i])
            else:
                rows.extend([r1[:] + filler[:]])
        if progress:
            cmdlineProgress.progress(ii)

        table.rows = rows
        return table

    def _postfixValues(self):
        "" # no autodoc ?

        """ finds postfixes 0, 1, .. in  __0, __1, ... in self.colNames
            an empty postfix "" is recognized as -1 """
        postfixes = set( getPostfix(c) for c in self.colNames )
        postfixes.discard(None) # internal cols starting witn __
        return [ -1 if p=="" else int(p[2:]) for p in postfixes ]

    def maxPostfix(self):
        return  max(self._postfixValues())

    def minPostfix(self):
        return  min(self._postfixValues())

    def findPostfixes(self):
        postfixes = set( getPostfix(c) for c in self.colNames )
        postfixes.discard(None) # internal cols starting with __
        return postfixes

    def incrementedPostfixes(self, by):
        newColNames = []
        for c in self.colNames:
            pf = getPostfix(c)
            if pf is not None:
                val = -1 if pf =="" else int(pf[2:])
                prefix = c if pf == "" else c.split("__")[0]
                newName = prefix+"__"+str(by+val)
                #print "val=%s prefix=%s newName=%s" % (val, prefix, newName)
            newColNames.append(newName)
        return newColNames

    def _buildJoinTable(self, t):

        incrementBy = self.maxPostfix()-t.minPostfix() + 1

        colNames = self.colNames + list(t.incrementedPostfixes(incrementBy))

        colFormats = self.colFormats + t.colFormats
        colTypes = self.colTypes + t.colTypes
        title = "%s vs %s" % (self.title, t.title)
        meta = {self: self.meta.copy(), t: t.meta.copy()}
        return Table(colNames, colTypes, colFormats, [], title, meta,
                     circumventNameCheck=True)

    def print_(self, w=8, out=None, title=None):
        """
        Prints the table to the console. ``w`` is the width of the columns,
        If you want to print to a file or stream instead, you can use the ``out``
        parameter, e.g. ``t.print_(out=sys.stderr)``.
        If you support a ``title`` string this will be printed above the
        content of the table.
        """
        if out is None:
            out = sys.stdout

        ix = [ i for i, f in enumerate(self.colFormats) if f is not None ]

        colwidths = []
        for i in ix:
            c = self.colNames[i]
            f = self.colFormatters[i]
            values = set(map(f, self.getColumn(c).values))
            values.discard(None)
            if values:
                mw = max(len(v) for v in values if v is not None)
            else:
                mw = 1 # for "-"
            colwidths.append(max(mw, len(c), w))


        #inner method is private, else the object can not be pickled !
        def _p(vals, colwidths=colwidths, out=out):
            for v, w in zip(vals, colwidths):
                expr = "%%-%ds" % w
                v = "-" if v is None else v
                print >> out, (expr % v),

        if title is not None:
            _p(len(title)*"=")
            print >> out
            _p([title])
            print >> out
            _p(len(title)*"=")
            print >> out


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

    _print = print_   # backwards compatibility

    def renamePostfixes(self, **kw):
        collected = dict()
        for postfix_old, postfix_new in kw.items():
            for c in self.colNames:
                if c.endswith(postfix_old):
                    c_new = c[:-len(postfix_old)]+postfix_new
                    collected[c]= c_new
        self.renameColumns(**collected)

    @staticmethod
    def toTable(colName, iterable,  format="", type_=None, title="", meta=None):
        """ generates a one-column table from an iterable, e.g. from a list,
            colName is name for the column.

            - if ``type_`` is not given a common type for all values is determined,
            - if ``format`` is not given, a default format for ``type_`` is used.

            further one can provide a title and meta data
        """
        if not isinstance(colName, str):
            raise Exception("colName is not a string. The arguments of this "\
                            "function changed in the past !")

        values = convert_list_to_overall_type(list(iterable))
        if type_ is None:
            type_ = common_type_for(values)
        if format == "":
            format = guessFormatFor(colName, type_) or "%r"
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
        print "features not integrated. I assume constant intensity"
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
