from Table import Table

class TableParser(object):

    separator = ";"   # column separator

    # headlines: a list with Nones and one string.
    # Nones stand for headlines which are ignored,
    # the string is split and the result are the
    # columnames
    headlines = []    

    types = []        # column types

    columnOffset = 0  # data starts in first column

    @staticmethod
    def checkHeadlineFields(h, f):
        return h==f

    @classmethod
    def parse(clz, lines):
        
        iter_ = iter(lines)
        for headline in clz.headlines:
            line = iter_.next().strip("\n")
            if headline is None: continue
            columnNames = headline.split(clz.separator)
            for h, f in zip(headline.split(clz.separator), line.split(clz.separator)):
                assert clz.checkHeadlineFields(h,f), "head line in file does not match specification"
          
        assert len(columnNames) == len(clz.types), "num columns is not the sames as num types"
        
        data = []
        for line in iter_:
            fields = line.strip("\n").split(clz.separator)[clz.columnOffset:]
            row = []
            for field, type_ in zip(fields, clz.types):
                row.append(type_(field))
            data.append(row)

        return Table(columnNames, clz.types, data)


class OldXCMSFeatureParser(TableParser):

     separator = " "
        
     headlines = ["mz mzmin mzmax rt rtmin rtmax into intf maxo maxf i sn sample"]

     types = [ float, float, float, float, float, float, float, float, float, float, int, float, int ]

     columnOffset = 1

     @staticmethod
     def checkHeadlineFields(h, f):
         # h is colname from specified headline, f is colname from file
         return h == f.strip('"')

class XCMSFeatureParser(object):

    
    typePrecedences = { int: (0, int) , float: (1, float), str: (2, str) }

    @classmethod
    def commonTypeOfColumn(clz, col):
        precedences = ( clz.typePrecedences[type(c)] for c in col )
        minprecedence=  min(precedences)
        return minprecedence[1]

    @classmethod
    def bestConvert(clz, val):
        try:
            return int(val)
        except ValueError:
            try:
                return float(val)
            except ValueError:
                return str(val)
  
    @classmethod
    def parse(clz, lines):
        columnNames = [ n.strip('"') for n in lines[0].split() ]
        numCol = len(columnNames)
        rows = []
        for line in lines[1:]:
            row= [XCMSFeatureParser.bestConvert(c) for c in line.split()[1:]]
            rows.append(row)

        if rows:
            columns     = ( (row[i] for row in rows) for i in range(numCol) )
            columnTypes = [XCMSFeatureParser.commonTypeOfColumn(col) for col in columns ] 
        else:
            columnTypes = numCol * (str, )
        return Table(columnNames, columnTypes, rows)

   




     
if __name__ == "__main__":
    
    table = XCMSFeatureParser.parse(file("output_from_xcms.csv").readlines())

