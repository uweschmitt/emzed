

def saveMap(ds, path=None):

    """ loads mzXML, mzML and mzData files """

    # local import in order to keep namespaces clean
    import os.path
    import libms.pyOpenMS, ms

    if path is None:
        path = ms.askForSave(extensions="mzML mzXML mzData".split())
        if path is None:
            return None

    _, ext = os.path.splitext(path)

    method = dict(MZXML = libms.pyOpenMS.saveMzXmlFile, 
                  MZML =  libms.pyOpenMS.saveMzMlFile, 
                  MZDATA= libms.pyOpenMS.saveMzDataFile).get(ext.upper()[1:])

    if method is None:
        raise Exception("unknown extension '%s' " % ext)

    method(ds, path)
    
