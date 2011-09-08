
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


    def addColumn(self, name, type_, value=None):
        for row in self.rows:
            row.append(value)
        self.colNames.append(name)
        self.colTypes.append(type_)

    
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
             
            

class FeatureTable(Table):

    def __init__(self, ds, colNames, colTypes, rows = None, colFormats = None, title=None):
        super(FeatureTable, self).__init__(colNames, colTypes, rows, colFormats, title)
        self.ds = ds

    @staticmethod
    def fromTableAndMap(table, ds):
        return FeatureTable(ds, table.colNames, table.colTypes, table.rows, table.colNames, table.title) 
