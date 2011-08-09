# -*- coding: utf-8 -*-

import mzExplorer
import pyOpenMS

ds = pyOpenMS.loadMzXMLFile("test.mzXML")
print "loaded ", len(ds), "specs"
mzExplorer.inspect(ds)