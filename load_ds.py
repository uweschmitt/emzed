# -*- coding: utf-8 -*-
"""
Created on Sun Aug 14 16:43:24 2011
@author: uwe schmitt
"""

import pyOpenMS

ds = pyOpenMS.loadMzXMLFile("test.mzXML")
print "loaded ", len(ds), "specs"
