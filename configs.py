#encoding: utf-8

# modules are searched in this order, search ends at first hit
# configs are read in this order, so local configs overrun global configs
repository_pathes = [ "C:/TMP", "$HOME/msworkbench_modules" ]


from libms.RConnect.XCMSConnector import CentwaveFeatureDetector, MatchedFilterFeatureDetector



cwfstd = CentwaveFeatureDetector.standardConfig
centwaveConfig = [   ("std", "standard config orbitrap", cwfstd) ]


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


mapAlignmentAlgorithmPoseClusteringConfig = [ ( "std", dict(nPeaks=100)) ]
dd = dict(gapcost=float(1), affinegapcost=float(0.5), scorefunction="s")
mapAlignmentAlgorithmSpectrumAlignmentConfig = [ ( "std", dd ) ]

import os.path

from string import Template

for p in repository_pathes:
    pp = os.path.join(Template(p).substitute(os.environ), "configs.py")
    if os.path.exists(pp):
        execfile(pp)
