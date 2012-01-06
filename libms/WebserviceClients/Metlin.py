#encoding:latin-1
import urllib, urllib2
import re
import csv
import cStringIO

from ..DataStructures.Table import Table

rootUrl = "http://metlin.scripps.edu/"
batchUrl = "http://metlin.scripps.edu/metabo_batch_list.php"
batchSize = 50

# inputmass is str ! so we can match later without floating
# points accuracy issues.
_defaultTypes  = dict(inputmass = str, mass=float, dppm=float)
_defaultFormats = dict(molid = "%s", inputmass="%s", adduct="%s",
                       mass = "%.6f", dppm="%f")

class MetlinMatcher(object):

    @staticmethod
    def _query(masses, ppm, polarity):
        for m in masses:
            assert isinstance(m, str), "masses must be passed as strings"
        dd = dict()
        dd["masses"] =  ",".join(masses)
        dd["ppm"] = ppm
        dd["modes"] = 1
        sign = { "+": " ", "-": "-" }[polarity]
        adducts =  ["M", "M%sH" % sign, "M%s2H" % sign]
        dd["formVar"]=",".join(adducts)
        data = dd.items()
        for add in adducts:
            data.append(("adducts", add))
        resp = urllib2.urlopen(batchUrl, urllib.urlencode(data))
        urlMatcher=re.search("temp/csv/batch\d+.csv", resp.read())
        assert urlMatcher is not None
        pathToCsv = urlMatcher.group()
        result = urllib.urlopen(rootUrl+pathToCsv)
        reader = csv.reader(cStringIO.StringIO(result.read()).readlines())
        header = reader.next()
        rows = list(reader)
        return header, rows

    @staticmethod
    def query(masses, ppm, polarity):
        allRows = []
        header = None
        for startIdx in range(0, len(masses), batchSize):
            massSlice = masses[startIdx:startIdx+batchSize]
            h, rows = MetlinMatcher._query(massSlice, ppm, polarity)
            if len(h) and len(h[0]):
                header = h
            allRows.extend(rows)

        if header is None:
            return None

        colNames = header
        colTypes = [ _defaultTypes.get(n, str) for n in colNames ]
        colFormats = [ _defaultFormats.get(n, "%s") for n in colNames ]
        transformedRows = []
        for row in allRows:
            row = [ t(v) for t,v in zip(colTypes, row) ]
            transformedRows.append(row)
        return Table(colNames, colTypes, colFormats, transformedRows,
                     title="metlin")




if 0:
    t = MetlinMatcher.query(["282.222813", "292.229272"], 50, "-")
    t.info()

    t._print()



