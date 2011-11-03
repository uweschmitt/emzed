import pyOpenMS as P
import operator, copy


def formatSeconds(seconds):

    hours = int(seconds / 3600)
    remainder = seconds %  3600   # % works for floating point !

    minutes = int(remainder / 60)
    seconds = remainder % 60  

    if hours:
        formatted = "%dh %dm %.1fs" % (hours, minutes, seconds)
    elif minutes:
        formatted = "%dm %.1fs" % (minutes, seconds)
    else:
        formatted = "%.1fs" % seconds
            
    return  formatted

def _formatter(f):
    """ toplevel helper for pickling """

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


    def __init__(self, colNames, colTypes, rows = None, colFormats = None, title=None, meta=None):
        assert len(colNames) == len(colTypes)
        if rows is not None:
            for row in rows:
                assert len(row) == len(colNames)
        self.colNames = colNames
        self.colTypes = colTypes
        self.rows     = rows
        self.colFormats = colFormats

        self.colIndizes = dict( (n, i) for i, n in enumerate(colNames)) 
        self.title = title
        self.meta = copy.deepcopy(meta) if meta is not None else dict()

        self.setup()
    
    def getVisibleCols(self):
        
        return [n  for (n, f) in zip (self.colNames, self.colFormats)  \
                              if f is not None ]

    def setup(self):
        self.colFormatters = [_formatter(f) for f in self.colFormats ]

    def __getstate__(self):
        """ for pickling. self.colFormatters can not be pickled """
        dd = self.__dict__.copy()
        del dd["colFormatters"]
        return dd

    def __setstate__(self, dd):
        self.__dict__ = dd
        self.setup()

    def __iter__(self):
        return iter(self.rows)

    def __getitem__(self, slice_):
        if not isinstance(slice_, slice):
            raise Exception("Table.[] needs slice as argument, got %r" % slice_)
        rows = self.rows.__getitem__(slice_)
        return Table(self.colNames, self.colTypes, rows, self.colFormats, self.title, self.meta)

    def extractRows(self, indices):
        rows = [ self.rows[i] for i in indices ]
        return Table(self.colNames, self.colTypes, rows, self.colFormats, self.title, self.meta)

    def requireColumn(self, name):
        if not name in self.colNames:
            raise Exception("column %r required" % name)
        return self

    def get(self, rowIdx, colName):
        return self.rows[rowIdx][self.getIndex(colName)]

    def getIndex(self, colName):
        idx = self.colIndizes.get(colName, None)
        if idx is None:
            raise Exception("colname %s not in table" % colName)
        return idx


    def sortBy(self, colName, ascending=True):
        idx = self.colIndizes[colName]
        self.rows.sort(key = operator.itemgetter(idx), reverse=not ascending)
        return self


    def addColumn(self, name, type_, value=None):
        for row in self.rows:
            row.append(value)
        self.colNames.append(name)
        self.colTypes.append(type_)
        return self
    
    def extractColumns(self, names):
        
        types = []
        formats  = []
        rows     = []

        indices = [ self.getIndex(name)  for name in names ]

        types = [ self.colTypes[i] for i in indices ]
        formats = [ self.colFormats[i] for i in indices ]


        for row in self.rows:
            rows.append( [ row[i] for i in indices ])
            
        return Table(names, types, rows, formats, self.title, self.meta)

    def __len__(self):
        return len(self.rows)

    def saveCSV(self, path):
        with file(path, "w") as fp:
            print >> fp, "; ".join(self.colNames)
            for row in self.rows:
                print >> fp, "; ".join(map(str, row))

        return self
             
            

class FeatureTable(Table):

    def __init__(self, ds, colNames, colTypes, rows = None, colFormats = None, title=None, meta = None):
        super(FeatureTable, self).__init__(colNames=colNames, 
                                           colTypes=colTypes, 
                                           rows=rows, 
                                           colFormats=colFormats, 
                                           title=title,
                                           meta=meta)
        self.requireColumn("mzmin")
        self.requireColumn("mzmax")
        self.requireColumn("mz")
        self.requireColumn("rt")
        self.requireColumn("rtmax")
        self.requireColumn("rtmax")

        self.ds = ds

    def toOpenMSFeatureMap(self):
        if not "area" in self.colNames:
            print "features not integrated. I assume const intensity"
            iarea = None
        else:
            iarea = self.getIndex("area")
        imz = self.getIndex("mz")
        irt = self.getIndex("rt")
        fm = P.FeatureMap()

        for row in self.rows:
            f = P.Feature()
            f.setMZ(row[imz])
            f.setRT(row[irt])
            if iarea is not None:
                f.setIntensity(row[iarea])
            else:
                f.setIntensity(1000.0)
            fm.push_back(f)
        return fm

    def alignAccordingTo(self, fmap):
        # test for matching
        assert fmap.size() == len(self)
        irt = self.getIndex("rt")
        irtmin = self.getIndex("rtmin")
        irtmax = self.getIndex("rtmax")
        for i in range(len(self)):
            feature = fmap[i]
            row = self.rows[i]
            rtold = row[irt]
            rnew  = feature.getRT()
            diff = rnew - rtold
            row[irt] += diff
            row[irtmin] += diff
            row[irtmax] += diff
        
        


    def extractColumns(self, colnames):
        rv = super(FeatureTable, self).extractColumns(colnames)
        return FeatureTable.fromTableAndMap(rv, self.ds)

    def extractRows(self, indizes):
        rv = super(FeatureTable, self).extractRows(indizes)
        return FeatureTable.fromTableAndMap(rv, self.ds)

    def __getitem__(self, slice_):
        rv = super(FeatureTable, self).__getitem__(slice_)
        return FeatureTable.fromTableAndMap(rv, self.ds)

    @staticmethod
    def fromTableAndMap(table, ds):
        meta = table.meta.copy()
        meta["source"] = ds.meta.get("source")

        return FeatureTable(ds, colNames=table.colNames,
                                colTypes=table.colTypes, 
                                rows=table.rows, 
                                colFormats=table.colFormats, 
                                title=table.title,
                                meta=table.meta) 
