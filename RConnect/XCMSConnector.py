from RExecutor import RExecutor
from pyOpenMS  import *


def installXCMSIfNeeded():

    script = """
                if (require("xcms") == FALSE) 
                {
                    source("http://bioconductor.org/biocLite.R")
                    biocLite("xcms", dep=T)
                }
            """

    RExecutor().run_commands(script)

installXCMSIfNeeded()

def XCMSPeakDetector(peakMap):

    assert isinstance(peakMap, PeakMap)

    """
        library(xcms)
        xset <- xcmsSet(%s)
        write.table(xset@peaks, file="%s")
    """
        
        
