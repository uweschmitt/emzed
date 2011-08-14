import sys
sys.path.insert(0, "..")

import pyOpenMS 
import sys

fileNameIn, fileNameOut = sys.argv[1:3]
scanMinIdx, scanMaxIdx = map(int, sys.argv[3:5])

assert scanMinIdx <= scanMaxIdx

print
print "load file"
peakMap = pyOpenMS.loadMzXmlFile(fileNameIn)

print "file loaded"

# scanMaxIdx is inclusive !
peakMap.specs = peakMap.specs[scanMinIdx:scanMaxIdx+1]

    
pyOpenMS.saveMzXmlFile(peakMap, fileNameOut)   
print "file saved"

    
    

