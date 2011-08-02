import sys
sys.path.insert(0, "..")

from pyOpenMS import *
import sys

fileNameIn, fileNameOut = sys.argv[1:3]
scanMinIdx, scanMaxIdx = map(int, sys.argv[3:5])

assert scanMinIdx <= scanMaxIdx

print
print "load file"
peakMap = loadMzXMLFile(fileNameIn)

print "file loaded"

# scanMaxIdx is inclusive !
peakMap.specs = peakMap.specs[scanMinIdx:scanMaxIdx+1]

    
saveMzXMLFile(peakMap, fileNameOut)   
print "file saved"

    
    

