#encoding: utf-8
from RExecutor import RExecutor
from ..DataStructures import *

import os

from ..intern_utils import TemporaryDirectoryWithBackup
from pyOpenMS import MSExperiment, FileHandler, String


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

class CentwaveFeatureDetector(object):

    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "centwave.txt")

    __doc__ = """ CentwaveFeatureDetector

    usage:

           print CentwaveFeatureDetector.standardConfig

           detector = CentwaveFeatureDetector(param1=val1, ....)
           detector.process(peakmap)


    Docs from XCMS library:

    """

    __doc__ += "".join(file(path).readlines())
    #__doc__ = unicode(__doc__, "latin-1").encode("latin-1")

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

        #installXcmsIfNeeded()

        self.config = self.standardConfig.copy()
        self.config.update(kw)

    def process(self, peakMap):
        assert isinstance(peakMap, PeakMap)
        if len(peakMap) == 0:
            raise Exception("empty peakmap")

        peakMap.spectra.sort(key = lambda s: s.rt)

        with TemporaryDirectoryWithBackup() as td:

            temp_input = os.path.join(td, "input.mzData")
            temp_output = os.path.join(td, "output.csv")

            FileHandler().storeExperiment(temp_input, peakMap.toMSExperiment())

            dd = self.config.copy()
            dd["temp_input"] = temp_input
            dd["temp_output"] = temp_output
            dd["fitgauss"] = str(dd["fitgauss"]).upper()
            dd["verbose_columns"] = str(dd["verbose_columns"]).upper()

            script = """
                        if (require("xcms") == FALSE)
                        {
                            source("http://bioconductor.org/biocLite.R")
                            biocLite("xcms", dep=T)
                        }
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
                raise Exception("R operation failed")

            # parse csv and shift rt related values to undo rt modifiaction
            # as described above
            table = XCMSFeatureParser.parse(file(temp_output).readlines())
            table.addConstantColumn("centwave_config", dd, dict, None)
            table.meta["generator"] = "xcms.centwave"
            decorate(table, peakMap)
            return table

class MatchedFilterFeatureDetector(object):

    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "matchedFilter.txt")

    __doc__ = u""" MatchedFilterFeatureDetector

    usage:

           print MatchedFilterFeatureDetector.standardConfig

           detector = MatchedFilterFeatureDetector(param1=val1, ....)
           detector.process(peakmap)


    Docs from XCMS library:

    """

    __doc__ += u"".join(file(path).readlines())
    #__doc__ = unicode(__doc__, "latin-1").encode("latin-1")

    standardConfig = dict(   fwhm = 30,
                             sigma = 30/2.3548,
                             max_ = 5,
                             snthresh = 10,
                             step = 0.1,
                             steps = 2,
                             mzdiff = 0.8 - 2*2,
                             index = False )

    def __init__(self, **kw):
        #installXcmsIfNeeded()
        self.config = self.standardConfig.copy()
        self.config.update(kw)

    def process(self, peakMap):
        assert isinstance(peakMap, PeakMap)
        if len(peakMap) == 0:
            raise Exception("empty peakmap")

        peakMap.spectra.sort(key = lambda s: s.rt)
        minRt = peakMap.spectra[0].rt
        # xcms does not like rt <= 0, so we shift that rt starts with 1.0:
        # we have to undo this shift later when parsing the output of xcms
        shift = minRt-1.0
        peakMap.shiftRt(-shift)

        with TemporaryDirectoryWithBackup() as td:

            temp_input = os.path.join(td, "input.mzData")
            temp_output = os.path.join(td, "output.csv")

            FileHandler().storeExperiment(temp_input, peakMap.toMSExperiment())

            dd = self.config.copy()
            dd["temp_input"] = temp_input
            dd["temp_output"] = temp_output
            dd["index"] = str(dd["index"]).upper()

            script = """
                        if (require("xcms") == FALSE)
                        {
                            source("http://bioconductor.org/biocLite.R")
                            biocLite("xcms", dep=T)
                        }
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

            # parse csv and
            table = XCMSFeatureParser.parse(file(temp_output).readlines())
            table.addConstantColumn("matchedfilter_config", dd, dict, None)
            table.meta["generator"] = "xcms.matchedfilter"
            decorate(table, peakMap)
            return table

def decorate(table, peakMap):
    table.addConstantColumn("peakmap", peakMap, object, None)
    src = peakMap.meta.get("source","")
    table.addConstantColumn("source", src, str, None)
    table.addConstantColumn("polarity", peakMap.polarity, str, None)
    table.addEnumeration()
    table.title = os.path.basename(src)
