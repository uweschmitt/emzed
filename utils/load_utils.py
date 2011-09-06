

def loadMap(path):

    # local import in order to keep namespaces clean
    import os.path
    import libms
    _, ext = os.path.splitext(path)

    method = dict(MZXML = libms.loadMzXmlFile, 
                  MZML =  libms.loadMzMlFile, 
                  MZDATA= libms.loadMzDataFile).get(ext.upper()[1:])

    if method is None:
        raise Exception("unknown extension '%s' " % ext)

    return method(path)
    
