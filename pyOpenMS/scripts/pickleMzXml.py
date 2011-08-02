import sys, cPickle
sys.path.insert(0, "..")

from pyOpenMS import *


fileNameIn, fileNameOut = sys.argv[1:3]

print
print "load file"
peakMap = loadMzXMLFile(fileNameIn)

print "file loaded"

cPickle.dump(peakMap, file(fileNameOut, "wb"))
    
    

