# -*- coding: utf-8 -*-
"""
Created on Sun Aug 14 16:43:24 2011
@author: uwe schmitt
"""

import ms

ds = ms.loadMzXmlFile("test.mzXML")

print "loaded ", len(ds), "specs"