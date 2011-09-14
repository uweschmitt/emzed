import sys
sys.path.insert(0, "../..")

import ms
import libms.DataStructures
import libms.Explorers
import numpy as np
import pylab

tab= libms.DataStructures.XCMSFeatureParser.fromCSV("test.csv")
ds=ms.loadMap("test.mzXML")
ftab = libms.DataStructures.FeatureTable.fromTableAndMap(tab, ds)

for row in ftab.rows:
    mzmin, mzmax = row[1:3]
    rtmin, rtmax = row[4:6]
    
    peaksl = [ spec.peaks for spec in ds.specs if rtmin <= spec.RT <=rtmax ]
    rts  = [ spec.RT for spec in ds.specs if rtmin <= spec.RT <=rtmax ]

    intensities = [ np.sum( (peaks[ (peaks[:,0] >= mzmin) * (peaks[:,0]<=mzmax)])[:,1]) for peaks in peaksl ]

    data = np.array(zip(rts, intensities))

    print data.shape
    np.savetxt("eic.csv", data, delimiter=";")


    
  



