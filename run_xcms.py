# -*- coding: utf-8 -*-

from RConnect import *
import pyOpenMS

ds = pyOpenMS.loadMzXmlFile("test.mzXML")
print "loaded ", len(ds), "specs"

t = XCMSPeakDetector(ds)

print t.colNames
print
print t.rows[0]
