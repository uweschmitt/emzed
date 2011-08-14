import sys, cPickle
sys.path.insert(0, "..")

import pyOpenMS 


fileNameIn, fileNameOut = sys.argv[1:3]

print
print "load file"
peakMap = pyOpenMS.loadMzXmlFile(fileNameIn)

print "file loaded"

cPickle.dump(peakMap, file(fileNameOut, "wb"))
    
    

