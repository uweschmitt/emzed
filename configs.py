#encoding: utf-8

from libms.RConnect.XCMSConnector import CentWaveFeatureDetector

def union(d1, d2):
    d = d1.copy()
    d.update(d2)
    return d

cwfstd = CentWaveFeatureDetector.standardConfig

centwaveConfigStd = dict( ppm=5, 
                          peakwidth=(15, 200),
                          prefilter=(3,1000), 
                          snthresh = 10, 
                          mzdiff=0.00 )


centwaveConfigLong= dict( ppm=5, 
                          peakwidth=(15, 600),
                          prefilter=(3,1000), 
                          snthresh = 10, 
                          mzdiff=0.00 )

centwaveConfig = [   ("std", "standard config orbitrap", union(cwfstd, centwaveConfigStd)) ,
                     ("long", "long retention config"  , union(cwfstd, centwaveConfigLong)) ,
                 ]


