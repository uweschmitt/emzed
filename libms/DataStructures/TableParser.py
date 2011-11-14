from Table import Table

class XCMSFeatureParser(object):

    typePrecedences = { int: (0, int) , float: (1, float), str: (2, str) }

    typeDefaults = dict( mz= float, mzmin= float, mzmax=float,
                      rt= float, rtmin= float, rtmax=float,
                      into= float, intb= float,
                      maxo= float, sn= float,
                      sample= int )

    standardFormats = { int: "%d", float : "%.2f", str: "%s" }

    formatDefaults = dict( mz= "%10.5f", mzmin= "%10.5f", mzmax= "%10.5f",
                           rt= "%6.1f",  rtmin= "%6.1f", rtmax = "%6.1f",
                           into= "%.2e", intb= "%.2e", intf="%.2e",
                           maxo= "%.2e", sn= "%.1e",
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

        return Table(columnNames, columnTypes, formats, rows)

    @classmethod
    def fromCSV(clz, path):
        lines = [ l.replace(";", " ") for l in file(path).readlines() ]
        modlines = [ '"%d" %s' % (i+1, l) for i, l in enumerate(lines[1:]) ]
        modlines.insert(0, lines[0])
        return clz.parse(modlines)

if __name__ == "__main__":
    table = XCMSFeatureParser.parse(file("output_from_xcms.csv").readlines())

