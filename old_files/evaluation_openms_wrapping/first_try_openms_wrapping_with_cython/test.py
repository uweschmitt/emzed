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

print "create spectrum: ",
spec = MSSpectrum1D()
print spec

print "RT is ", spec.getRT()
print "setRT(3.2)"
spec.setRT(3.2)
print "RT is ", spec.getRT()

print "MSLevel is ", spec.getMSLevel()
print "setMSLevel(32)"
spec.setMSLevel(32)
print "MSLevel is ", spec.getMSLevel()

print "Name is ", spec.getName()
print "setName('test')"
spec.setName('test')
print "Name is ", spec.getName()

mse = MSExperiment1D()
mse.get2DData()
