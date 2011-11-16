import sys
sys.path.insert(0, "..")
import libms
import ms


print "load"
ds = ms.loadPeakMap("test.mzXML")
print "loaded"
det = libms.RConnect.CentwaveFeatureDetector(ppm=3, peakwidth=(8, 15), snthresh=40, prefilter=(8, 10000), mzdiff=1.5 )
table = det.process(ds)

table.store("features.table", True)

