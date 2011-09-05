import ms

ds = ms.loadMzXmlFile("../unittests/data/test.mzXML")
det = ms.CentWaveFeatureDetector(ppm=3, peakwidth=(8, 13), snthresh=40, prefilter=(8, 10000), mzdiff=1.5 )
help(det)
table = det.process(ds)

table.saveCSV("centwaveResult.csv")

print len(table), "features found"

ms.viewTable(table)
