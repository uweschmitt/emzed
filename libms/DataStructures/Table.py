import operator 

class Table(object):

    def __init__(self, colNames, colTypes, rows = None, colFormats = None, title=None):
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
        self.setupFormatters()

    def setupFormatters(self):
        self.colFormatters = [ (lambda s,f=f: f % s) if isinstance(f, str) \
                                              else f for f in self.colFormats ]


    def __getstate__(self):
        """ for pickling. self.colFormatters can not be pickled """
        dd = self.__dict__.copy()
        del dd["colFormatters"]
        return dd

    def __setstate__(self, dd):
        self.__dict__ = dd
        self.setupFormatters()

    def __iter__(self):
        return iter(self.rows)

    def __getitem__(self, ix):
        rows = self.rows.__getitem__(ix)
        return Table(self.colNames, self.colTypes, rows, self.colFormats, self.title)

    def requireColumn(self, name):
        if not name in self.colNames:
            raise Exception("column %r required" % name)
        return self

    def get(self, rowIdx, colName):
        ix = self.colIndizes[colName]
        return self.rows[rowIdx][ix]

    def getIndex(self, colName):
        return self.colIndizes[colName]

    def restrictToColumns(self, *names):
        
        colIndizes = []
        for i, colName in enumerate(self.colNames):
            if colName in names:
                colIndizes.append(i)

        # rebuilt, as there may be names in *names which
        # are not present in this table
        colNames = [ self.colNames[i] for i in colIndizes ]

        colTypes = [ self.colTypes[i] for i in colIndizes ]
        colFormats= [ self.colFormats[i] for i in colIndizes ]
        
        rows = [ [ row[i] for i in colIndizes ] for row in self.rows ]

        return Table(colNames, colTypes, rows, colFormats, self.title)


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

    
    def evaluateMacros(self):
        pass

        # TODO: ColTypes: dataCell, evalCell. letztere mit ergebnistyp
        
            #if type_ == "@expr":
            #   dd = dict( (n, row[self.colIndizes[n]]) for n in self.colNames )
            #   row.append(eval(value, dd))
            #else:

    def extractColumns(self, *names):
        
        colNames = []
        colTypes = []
        rows     = []

        for name in names:
            if not name in self.colIndizes.keys():
                raise Exception("column %r does not exist in %r" % (name, self)) 
            colNames.append(name)
            colTypes.append(self.colIndizes[name])

        for row in self.rows:
            rows.append( [ row[self.colIndizes[name]] for name in names ])
            
        return Table(colNames, colTypes, rows)

    def __len__(self):
        return len(self.rows)

    def saveCSV(self, path):
        with file(path, "w") as fp:
            print >> fp, "; ".join(self.colNames)
            for row in self.rows:
                print >> fp, "; ".join(map(str, row))

        return self
             
            

class FeatureTable(Table):

    def __init__(self, ds, colNames, colTypes, rows = None, colFormats = None, title=None):
        super(FeatureTable, self).__init__(colNames=colNames, 
                                           colTypes=colTypes, 
                                           rows=rows, 
                                           colFormats=colFormats, 
                                           title=title)
        self.requireColumn("mzmin")
        self.requireColumn("mzmax")
        self.requireColumn("mz")
        self.requireColumn("rt")
        self.requireColumn("rtmax")
        self.requireColumn("rtmax")

        self.ds = ds

    def __getitem__(self, ix):
        rows = self.rows.__getitem__(ix)
        return FeatureTable(self.ds, self.colNames, self.colTypes, rows, self.colFormats, self.title)

    def restrictToColumns(self, *colnames):
        rv = super(FeatureTable, self).restrictToColumns(*colnames)
        rv.ds = self.ds
        return rv

    @staticmethod
    def fromTableAndMap(table, ds):
        return FeatureTable(ds, colNames=table.colNames,
                                colTypes=table.colTypes, 
                                rows=table.rows, 
                                colFormats=table.colFormats, 
                                title=table.title) 
