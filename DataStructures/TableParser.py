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


class XCMSFeatureParser(TableParser):

     separator = " "
        
     headlines = ["mz mzmin mzmax rt rtmin rtmax into intf maxo maxf i sn sample"]

     types = [ float, float, float, float, float, float, float, float, float, float, int, float, int ]

     columnOffset = 1

     @staticmethod
     def checkHeadlineFields(h, f):
         # h is colname from specified headline, f is colname from file
         return h == f.strip('"')

     
if __name__ == "__main__":
    
    table = XCMSFeatureParser.parse(file("output_from_xcms.csv").readlines())

