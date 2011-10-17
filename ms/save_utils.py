

def storeExperiment(ds, path=None):

    """ saves mzXML, mzML and mzData files """

    # local import in order to keep namespaces clean
    import os.path
    import ms
    from pyOpenMS import MSExperiment, FileHandler

    if path is None:
        path = ms.askForSave(extensions="mzML mzXML mzData".split())
        if path is None:
            return None

    experiment = MSExperiment()
    fh  = FileHandler()
    fh.storeExperiment(path, experiment)
    
