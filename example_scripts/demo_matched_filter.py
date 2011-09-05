
import ms

ds = ms.loadMzXmlFile("../unittests/data/test.mzXML")




det = ms.MatchedFilterFeatureDetector()

print
print det.standardConfig

print

#help(det)
table = det.process(ds)
print len(table), "features found"

table.saveCSV("matchedFilterResult.csv")

ms.viewTable(table)
