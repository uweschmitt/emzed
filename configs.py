#encoding: utf-8


from libms.RConnect.XCMSConnector import CentwaveFeatureDetector, MatchedFilterFeatureDetector

cwfstd = CentwaveFeatureDetector.standardConfig
centwaveConfig = [   ("std", "standard config orbitrap", cwfstd) ]


mfstd = MatchedFilterFeatureDetector.standardConfig
matchedFilterConfig = [  ( "std", "standard config" , mfstd ) ]


from libms.PeakPicking import PeakPickerHiRes

peakPickerHiResConfig = [ ("std", "orbitrap standard", PeakPickerHiRes.standardConfig) ]


from libms.PeakIntegration import *
# key "std" must exist !
peakIntegrators = [ ( "sgolay",        SGIntegrator(window_size=11, order=2) ) ,
                    ( "asym_gauss", AsymmetricGaussIntegrator() ) ,
                    ( "trapez", TrapezIntegrator() ) ,
                    ( "emg_exact", SimplifiedEMGIntegrator() ) ,
                    ( "no_integration", NoIntegration() ) ,
                   ]



import os.path

from string import Template

# modules are searched in this order, search ends at first hit
# configs are read in this order, so local configs overrun global configs

import userConfig
repositoryPathes = [ userConfig.getExchangeFolder(), userConfig.getDataHome() ]


for p in repositoryPathes:
    pp = os.path.join(Template(p).substitute(os.environ), "local_configs.py")
    if os.path.exists(pp):
        print "RUN FILE", pp
        dd = locals()
        dd["is_exec"]=True
        execfile(pp, globals(), dd)
