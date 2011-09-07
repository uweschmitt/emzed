from RExecutor import RExecutor
from ..pyOpenMS  import *
from ..DataStructures import *

import os

from ..intern_utils import TemporaryDirectoryWithBackup


def installXcmsIfNeeded():

    R_LIBS = os.environ.get("R_LIBS")
    if R_LIBS == None:
        LLL.error("R_LIBS not set in environment")
        raise Exception("inconsistent system: R_LIBS not set.")

    if os.path.exists(os.path.join(R_LIBS, "xcms")):  
        return
    
    script = """
                if (require("xcms") == FALSE) 
                {
                    source("http://bioconductor.org/biocLite.R")
                    biocLite("xcms", dep=T)
                }
            """
    RExecutor().run_command(script)


def lookForXcmsUpgrades():

    script = """
                 source("http://bioconductor.org/biocLite.R")
                 todo <- old.packages(repos=biocinstallRepos())
                 q(status=length(todo))
             """
    num = RExecutor().run_command(script)
    if not num:
        print "No update needed"
    else:
        print num, "updates found"

def doXcmsUpgrade():

    script = """
                 source("http://bioconductor.org/biocLite.R")
                 todo <- update.packages(repos=biocinstallRepos(), ask=FALSE, checkBuilt=TRUE)
                 q(status=length(todo))
             """
    return RExecutor().run_command(script)

class CentWaveFeatureDetector(object):

    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "centwave.txt")

    __doc__ = """ CentWaveFeatureDetector

    usage:

           print CentWaveFeatureDetector.standardConfig  

           detector = CentWaveFeatureDetector(param1=val1, ....)
           detector.process(peakmap)

    
    Docs from XCMS library:

    """

    __doc__ += "".join(file(path).readlines())

    standardConfig = dict(   ppm=25, 
                             peakwidth=(20,50), 
                             prefilter=(3,100), 
                             snthresh = 10, 
                             integrate = 1,
                             mzdiff=-0.001, 
                             noise=0,
                             mzCenterFun="wMean",
                             fitgauss=False,
                             verbose_columns = False )

    def __init__(self, **kw):
        self.config = self.standardConfig.copy()
        self.config.update(kw)

    def process(self, peakMap):
        assert isinstance(peakMap, PeakMap)
        
        with TemporaryDirectoryWithBackup() as td:

            temp_input = os.path.join(td, "input.mzData")
            temp_output = os.path.join(td, "output.csv")

            saveMzDataFile(peakMap, temp_input)

            dd = self.config.copy()
            dd["temp_input"] = temp_input
            dd["temp_output"] = temp_output
            dd["fitgauss"] = str(dd["fitgauss"]).upper()
            dd["verbose_columns"] = str(dd["verbose_columns"]).upper()
        
            script = """
                        library(xcms)
                        xs <- xcmsSet(%(temp_input)r, method="centWave", 
                                          ppm=%(ppm)d, 
                                          peakwidth=c%(peakwidth)r,
                                          prefilter=c%(prefilter)r,
                                          snthresh = %(snthresh)f,
                                          integrate= %(integrate)d,
                                          mzdiff   = %(mzdiff)f,
                                          noise    = %(noise)f,
                                          fitgauss = %(fitgauss)s,
                                          verbose.columns = %(verbose_columns)s,
                                          mzCenterFun = %(mzCenterFun)r
                                     )
                        write.table(xs@peaks, file=%(temp_output)r)
                        q(status=4711)
                     """ % dd

            if RExecutor().run_command(script, td) != 4711:
                raise Exception("R opreation failed")

            return XCMSFeatureParser.parse(file(temp_output).readlines())

            
class MatchedFilterFeatureDetector(object):

    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "matchedFilter.txt")

    __doc__ = """ MatchedFilterFeatureDetector

    usage:

           print MatchedFilterFeatureDetector.standardConfig  

           detector = MatchedFilterFeatureDetector(param1=val1, ....)
           detector.process(peakmap)

    
    Docs from XCMS library:

    """

    __doc__ += "".join(file(path).readlines())

    standardConfig = dict(   fwhm = 30,
                             sigma = 30/2.3548,
                             max_ = 5,
                             snthresh = 10,
                             step = 0.1,
                             steps = 2,
                             mzdiff = 0.8 - 2*2,
                             index = False )

    def __init__(self, **kw):
        self.config = self.standardConfig.copy()
        self.config.update(kw)

    def process(self, peakMap):
        assert isinstance(peakMap, PeakMap)
        
        with TemporaryDirectoryWithBackup() as td:

            temp_input = os.path.join(td, "input.mzData")
            temp_output = os.path.join(td, "output.csv")

            saveMzDataFile(peakMap, temp_input)

            dd = self.config.copy()
            dd["temp_input"] = temp_input
            dd["temp_output"] = temp_output
            dd["index"] = str(dd["index"]).upper()
        
            script = """
                        library(xcms)
                        xs <- xcmsSet(%(temp_input)r, method="matchedFilter", 
                                       fwhm = %(fwhm)f, sigma = %(sigma)f,
                                       max = %(max_)d,
                                       snthresh = %(snthresh)f,
                                       step = %(step)f, steps=%(steps)d,
                                       mzdiff = %(mzdiff)f,
                                       index = %(index)s,
                                       sleep=0
                                     )
                        write.table(xs@peaks, file=%(temp_output)r)
                        q(status=4711)
                     """ % dd

            if RExecutor().run_command(script, td) != 4711:
                raise Exception("R opreation failed")

            return XCMSFeatureParser.parse(file(temp_output).readlines())

