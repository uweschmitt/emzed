from RExecutor import RExecutor
from pyOpenMS  import *
from DataStructures import *

import os

from utils import TemporaryDirectoryWithBackup


def installXcmsIfNeeded():

    R_LIBS = os.environ.get("R_LIBS")
    if R_LIBS == None:
        LLL.error("R_LIBS not set in environment")
        raise Exception("inconsistent system: R_LIBS not set.")

    print os.path.join(R_LIBS, "xcms")
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

def XCMSPeakDetector(peakMap):

    assert isinstance(peakMap, PeakMap)
    
    with TemporaryDirectoryWithBackup() as td:

        temp_input = os.path.join(td, "input.mzXml")
        temp_output = os.path.join(td, "output.csv")

        saveMzXmlFile(peakMap, temp_input)
    
        script = """
                    library(xcms)
                    xs <- xcmsSet(%r)
                    write.table(xs@peaks, file=%r)
                    q(status=4711)
                 """ % (temp_input, temp_output)

        if RExecutor().run_command(script, td) != 4711:
            raise Exception("R opreation failed")

        return XCMSFeatureParser.parse(file(temp_output).readlines())

        
