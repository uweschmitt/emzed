
from ..pyOpenMS import *
import os.path

def loadMap(path):
    _, ext = os.path.splitext(path)

    method = dict(MZXML = loadMzXmlFile, 
                  MZML = loadMzMlFile, 
                  MZDATA=loadMzDataFile).get(ext.upper()[1:])

    if method is None:
        raise Exception("unknown extension %s" % ext)

    return method(path)
    
