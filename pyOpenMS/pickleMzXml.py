
from pyOpenMS import *
import sys, cPickle


fileNameIn, fileNameOut = sys.argv[1:3]

print
print "load file"
peakMap = loadMzXMLFile(fileNameIn)

print "file loaded"

cPickle.dump(peakMap, file(fileNameOut, "wb"))
    
    

