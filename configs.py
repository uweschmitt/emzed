#encoding: utf-8

repository_pathes = [ "C:/TMP", "$HOME/msworkbench_modules" ]


from libms.RConnect.XCMSConnector import CentwaveFeatureDetector, MatchedFilterFeatureDetector


"""
def union(d1, d2):
    d = d1.copy()
    d.update(d2)
    return d
"""

cwfstd = CentwaveFeatureDetector.standardConfig
centwaveConfig = [   ("std", "standard config orbitrap", cwfstd) ]

"""
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

"""


mfstd = MatchedFilterFeatureDetector.standardConfig
matchedFilterConfig = [  ( "std", "standard config" , mfstd ) ]


from libms.PeakPicking import PeakPickerHiRes

peakPickerHiResConfig = [ ("std", "orbitrap standard", PeakPickerHiRes.standardConfig) ]


from libms.PeakIntegration import *
# key "std" must exist !
peakIntegrators = [ ( "std",        SGIntegrator(window_size=11, order=2) ) ,
                    ( "asym_gauss", AsymmetricGaussIntegrator(gtol=0.1) ) ,
                    ( "asym_gauss_exakt", AsymmetricGaussIntegrator(gtol=None) ) ,
                    ( "trapez", TrapezIntegrator() ) ,
                   ]


import os.path

from string import Template

for p in repository_pathes:
    pp = os.path.join(Template(p).substitute(os.environ), "configs.py")
    if os.path.exists(pp):
        execfile(pp)
