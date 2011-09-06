

def loadMap(path):

    # local import in order to keep namespaces clean
    import os.path
    import ms
    _, ext = os.path.splitext(path)

    method = dict(MZXML = ms.loadMzXmlFile, 
                  MZML =  ms.loadMzMlFile, 
                  MZDATA= ms.loadMzDataFile).get(ext.upper()[1:])

    if method is None:
        raise Exception("unknown extension '%s' " % ext)

    return method(path)
    
