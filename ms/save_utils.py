

def storePeakMap(pm, path=None):

    """ saves mzXML, mzML and mzData files """

    # local import in order to keep namespaces clean
    import ms
    from pyOpenMS import FileHandler

    if path is None:
        path = ms.askForSave(extensions="mzML mzXML mzData".split())
        if path is None:
            return None

    experiment = pm.toMSExperiment()
    fh  = FileHandler()
    fh.storeExperiment(path, experiment)

def storeTable(tab, path=None):
    """ saves .table files """

    # local import in order to keep namespaces clean
    import ms

    if path is None:
        path = ms.askForSave(extensions=["table"])
        if path is None:
            return None

    tab.store(path)
