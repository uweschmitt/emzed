

def loadMap(path=None):

    """ loads mzXML, mzML and mzData files """

    # local import in order to keep namespaces clean
    import os.path
    import libms.pyOpenMS, ms

    if path is None:
        path = ms.askForSingleFile(extensions="mzML mzXML mzData".split())
        if path is None:
            return None

    _, ext = os.path.splitext(path)

    method = dict(MZXML = libms.pyOpenMS.loadMzXmlFile, 
                  MZML =  libms.pyOpenMS.loadMzMlFile, 
                  MZDATA= libms.pyOpenMS.loadMzDataFile).get(ext.upper()[1:])

    if method is None:
        raise Exception("unknown extension '%s' " % ext)

    return method(path)
    
