from RConnect import *
from pyOpenMS import *
from FeatureExplorer import *

ds = loadMzXmlFile("../unittests/data/test.mzXML")
det = CentWaveFeatureDetector(ppm=3, peakwidth=(8, 13), snthresh=40, prefilter=(8, 10000), mzdiff=1.5 )
help(det)
table = det.process(ds)
print len(table), "features found"

viewTable(table)
