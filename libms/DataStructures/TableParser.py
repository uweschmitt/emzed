import Table

class TableParser(object):

    @classmethod
    def parse(clz, lines):
        columnNames = [ n.strip('"') for n in lines[0].split() ]
        numCol = len(columnNames)
        rows = []
        for line in lines[1:]:
            row= [Table.bestConvert(c) for c in line.split()[1:]]
            rows.append(row)

        if rows:
            columns     = ( (row[i] for row in rows) for i in range(numCol) )
            columnTypes = [Table.common_type_for(col) for col in columns ]
            knownTypes = [ (i, clz.typeDefaults.get(columnNames[i] )) for i in range(numCol) ]

            for i, type_ in knownTypes:
                if type_ is not None:
                    columnTypes[i] = type_

            formats     = [Table.standardFormats[type_] for type_ in columnTypes]
            knownFormats = [ (i, clz.formatDefaults.get(columnNames[i] )) for i in range(numCol) ]

            for i, format_ in knownFormats:
                if format_ is not None:
                    formats[i] = format_

            for i, row in enumerate(rows):
                rows[i] = [ t(v) if t is not object else v  for (t, v) in  zip(columnTypes, row) ] 


        else:
            columnTypes = numCol * (str, )
            formats     = numCol * ("%r", )

        return Table.Table(columnNames, columnTypes, formats, rows)

class XCMSFeatureParser(TableParser):


    typeDefaults = dict( mz= float, mzmin= float, mzmax=float,
                      rt= float, rtmin= float, rtmax=float,
                      into= float, intb= float,
                      maxo= float, sn= float,
                      sample= int )

    formatSeconds = Table.fms
    formatDefaults = dict( mz= "%10.5f", mzmin= "%10.5f", mzmax= "%10.5f",
                           rt=  formatSeconds, rtmin=formatSeconds,
                           rtmax=formatSeconds, into= "", intb= "", intf="",
                           maxo= "", sn= "%.1e",
                           sample= "")


