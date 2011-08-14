import sys
sys.path.insert(0, "..")

import pyOpenMS 

ff = pyOpenMS.FeatureFinder("centroided").updateParams(dict(debug="false"))
ds = pyOpenMS.loadMzXmlFile(r"tests\data\READW_MS2_dataset.mzXML")

print "got data"
print len(ds), "specs"

ds_level1 = ds.filter(lambda s: s.msLevel == 1)

print len(ds_level1), "specs with ms level 1"

feats = ff.run(ds_level1)

print len(feats), "features"
