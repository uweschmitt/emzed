import pyOpenMS as P
import operator, copy, os# , itertools


def formatSeconds(seconds):
    return "%.2fm" % (seconds / 60.0)

def _formatter(f):
    """ helper, is toplevel for supporting pickling of Table """

    if f is None:
        def format(s):
            return None
    elif f.startswith("%"):
        def format(s, f=f):
            return f%s
    else:
        def format(s, f=f):
            return eval(f, globals(), dict(o=s))
    return format



class Table(object):

    def __init__(self, colNames, colTypes, colFormats, rows=None, title=None,
                       meta=None, sources=None):
        assert len(colNames) == len(colTypes)
        if rows is not None:
            for row in rows:
                assert len(row) == len(colNames)
        self.colNames = list(colNames)
        self.colTypes = list(colTypes)
        self.rows     = rows
        self.colFormats = list(colFormats)

        self.colIndizes = dict((n, i) for i, n in enumerate(colNames))
        self.title = title
        self.meta = copy.deepcopy(meta) if meta is not None else dict()
        self.sources = () if sources is None else tuple(sources)
        self.setupFormatters()

    def getVisibleCols(self):
        return [n for (n, f) in zip (self.colNames, self.colFormats)\
                              if f is not None ]

    def setupFormatters(self):
        self.colFormatters = [_formatter(f) for f in self.colFormats ]

    def __getstate__(self):
        """ for pickling. self.colFormatters can not be pickled """
        dd = self.__dict__.copy()
        del dd["colFormatters"]
        return dd

    def __getattr__(self,name):
        if name in self.colNames:
            ix = self.getIndex(name)
            column = [ row[ix] for row in self.rows ]
            return column
        raise AttributeError("%s has no attribute %s" % (self, name))

    def __setstate__(self, dd):
        self.__dict__ = dd
        self.setupFormatters()

    def __iter__(self):
        return iter(self.rows)

    def requireColumn(self, name):
        if not name in self.colNames:
            raise Exception("column %r required" % name)
        return self

    def getIndex(self, colName):
        idx = self.colIndizes.get(colName, None)
        if idx is None:
            raise Exception("colname %s not in table" % colName)
        return idx

    def addEnumeration(self, colname="id"):
        if colname in self.colNames:
            raise Exception("column with name %s already exists")

        self.colNames.insert(0, colname)
        self.colTypes.insert(0, int)
        self.colFormats.insert(0, "%d")
        for i, r in enumerate(self.rows):
            r.insert(0, i)
        self.setupFormatters()
        return self

    def sortBy(self, colName, ascending=True):
        idx = self.colIndizes[colName]
        self.rows.sort(key = operator.itemgetter(idx), reverse=not ascending)
        if ascending:
            self.primaryIndex = {colName: True}
        else:
            self.primaryIndex = {}
        return self

    def addConstantColumn(self, name, type_, format, value=None):
        # HIER MIT EXPRESSION !
        for row in self.rows:
            row.append(value)
        self.colNames.append(name)
        self.colTypes.append(type_)
        self.colFormats.append(format)
        self.setupFormatters()
        return self

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
        return self

    def __len__(self):
        return len(self.rows)

    def storeCSV(self, path):
        if not os.path.splitext(path)[1].upper()==".CSV":
            raise Exception("%s has wrong filentype extensioe" % path)
        it = itertools
        for p in it.chain([path], ( "%s.%d" % (path, i) for i in it.count(1))):
            if not os.path.exists(p):
                print "write ", p
                with file(p, "w") as fp:
                    print >> fp, "; ".join(self.colNames)
                    for row in self.rows:
                        print >> fp, "; ".join(map(str, row))
                break
        return self


def requireFeatures(table):
    table.requireColumn("mzmin")
    table.requireColumn("mzmax")
    table.requireColumn("mz")
    table.requireColumn("rt")
    table.requireColumn("rtmax")
    table.requireColumn("rtmax")

def toOpenMSFeatureMap(table):
    table.requireFeatures()
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
