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

    typeDefaults = dict( mz= float, mzmin= float, mzmax=float,
                      rt= float, rtmin= float, rtmax=float,
                      into= float, intb= float,
                      maxo= float, sn= float,
                      sample= int )

    standardFormats = { int: "%d", float : "%.2f", str: "%s" }

    formatDefaults = dict( mz= "%10.5f", mzmin= "%10.5f", mzmax= "%10.5f",
                           rt= "%6.2f", rtmin= "%6.2f", rtmax= "%6.2f",
                           into= "%.2e", intb= "%.2e",
                           maxo= "%.2e", sn= "%5.1f",
                           sample= "%2d" )

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
            row= [clz.bestConvert(c) for c in line.split()[1:]]
            rows.append(row)

        if rows:
            columns     = ( (row[i] for row in rows) for i in range(numCol) )
            columnTypes = [clz.commonTypeOfColumn(col) for col in columns ] 
            
            knownTypes = [ (i, clz.typeDefaults.get(columnNames[i] )) for i in range(numCol) ]

            for i, type_ in knownTypes:
                if type_ is not None:
                    columnTypes[i] = type_

            formats     = [clz.standardFormats[type_] for type_ in columnTypes]

            knownFormats = [ (i, clz.formatDefaults.get(columnNames[i] )) for i in range(numCol) ]

            for i, format_ in knownFormats:
                if format_ is not None:
                    formats[i] = format_
            
        else:
            columnTypes = numCol * (str, )
            formats     = numCol * ("%r", )

        return Table(columnNames, columnTypes, rows, formats)

   




     
if __name__ == "__main__":
    
    table = XCMSFeatureParser.parse(file("output_from_xcms.csv").readlines())

