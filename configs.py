#encoding: utf-8

from libms.RConnect.XCMSConnector import CentwaveFeatureDetector, MatchedFilterFeatureDetector

import ms

def union(d1, d2):
    d = d1.copy()
    d.update(d2)
    return d

cwfstd = CentwaveFeatureDetector.standardConfig

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


mfstd = MatchedFilterFeatureDetector.standardConfig
matchedFilterStd = dict ( )
matchedFilterConfig = [  ( "std", "standard config" , mfstd ) ]


pathToProteoWizard = r"C:\Dokumente und Einstellungen\Administrator\Eigene Dateien\proteowizard"


from libms.PeakIntegration import *
# key "std" must exist !
PeakIntegrators = dict( std     = SGIntegrator(window_size=11, order=2),
                        sg_21_2 = SGIntegrator(window_size=21, order=2),
                        sg_11_1 = SGIntegrator(window_size=11, order=1),
                        sg_21_1 = SGIntegrator(window_size=21, order=1),
                        asym_gauss = AssymetricGaussIntegrator(),
                      )

