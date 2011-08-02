import sys
sys.path.insert(0, "..")

from pyOpenMS import *
import sys

fileNameIn, fileNameOut = sys.argv[1:3]

print
print "load file"
peakMap = loadMzXMLFile(fileNameIn)

print "file loaded"

peaksBefore = 0
peaksAfter  = 0

for spec in peakMap:
    peaksBefore += len(spec)
    spec.peaks = spec.peaks[spec.peaks[:,1]>0]
    peaksAfter += len(spec)

print
print "peaks before zero removal :", peaksBefore
print "peaks after zero removal  :", peaksAfter
print
    
saveMzXMLFile(peakMap, fileNameOut)   
print "file saved"

    
    

