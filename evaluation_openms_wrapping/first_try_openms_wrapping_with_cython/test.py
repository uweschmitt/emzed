from pyOpenMS import *

print "create Feature: ",
f = Feature()
print f

print "create FeatureMap: ",
fm = FeatureMap()
print fm

print "FeatureMap has ",
print len(fm),
print "elements"

print "add Feature"
fm.push_back(f)

print "Now FeatureMap has ",
print len(fm),
print "elements"
