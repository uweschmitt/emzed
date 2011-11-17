import Table

class TableParser(object):



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
            columnTypes = [Table._commonTypeOfColumn(col) for col in columns ]
            knownTypes = [ (i, clz.typeDefaults.get(columnNames[i] )) for i in range(numCol) ]

            for i, type_ in knownTypes:
                if type_ is not None:
                    columnTypes[i] = type_

            formats     = [Table._standardFormats[type_] for type_ in columnTypes]
            knownFormats = [ (i, clz.formatDefaults.get(columnNames[i] )) for i in range(numCol) ]

            for i, format_ in knownFormats:
                if format_ is not None:
                    formats[i] = format_
        else:
            columnTypes = numCol * (str, )
            formats     = numCol * ("%r", )

        return Table.Table(columnNames, columnTypes, formats, rows)

    @classmethod
    def fromCSV(clz, path):
        lines = [ l.replace(";", " ") for l in file(path).readlines() ]
        modlines = [ '"%d" %s' % (i+1, l) for i, l in enumerate(lines[1:]) ]
        modlines.insert(0, lines[0])
        return clz.parse(modlines)

class XCMSFeatureParser(TableParser):


    typeDefaults = dict( mz= float, mzmin= float, mzmax=float,
                      rt= float, rtmin= float, rtmax=float,
                      into= float, intb= float,
                      maxo= float, sn= float,
                      sample= int )

    fms = "'%.2fm' % (o/60.0)"
    formatDefaults = dict( mz= "%10.5f", mzmin= "%10.5f", mzmax= "%10.5f",
                           rt=  fms, rtmin=fms, rtmax=fms,
                           into= "", intb= "", intf="",
                           maxo= "", sn= "%.1e",
                           sample= "")

if __name__ == "__main__":
    table = XCMSFeatureParser.parse(file("output_from_xcms.csv").readlines())

