from RExecutor import RExecutor
from pyOpenMS  import *

import os


def installXCMSIfNeeded():

    R_LIBS = os.environ.get("R_LIBS")
    if R_LIBS == None:
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
    RExecutor().run_commands(script)


def lookForXmcsUpgrades():

    script = """
                 source("http://bioconductor.org/biocLite.R")
                 todo <- old.packages(repos=biocinstallRepos())
                 q(status=length(todo))
             """
    num = RExecutor().run_commands(script)
    if not num:
        print "No update needed"
    else:
        print num, "updates found"

def doXmcsUpgrade():

    script = """
                 source("http://bioconductor.org/biocLite.R")
                 todo <- update.packages(repos=biocinstallRepos(), ask=FALSE, checkBuilt=TRUE)
                 q(status=length(todo))
             """
    return RExecutor().run_commands(script)

def XCMSPeakDetector(peakMap):

    assert isinstance(peakMap, PeakMap)

    """
        library(xcms)
        xset <- xcmsSet(%s)
        write.table(xset@peaks, file="%s")
    """
        
