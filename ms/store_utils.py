

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

def storeTable(tab, path=None, forceOverwrite=False):
    """ saves .table files

        If path is not provided, a file dialog opens
        for choosing the files name and location.
    """

    # local import in order to keep namespaces clean
    import ms

    if path is None:
        startAt = tab.meta.get("loaded_from", "")
        path = ms.askForSave(extensions=["table"], startAt=startAt)
        if path is None:
            return None
    tab.store(path, forceOverwrite)

def storeCSV(tab, path=None):

    # local import in order to keep namespaces clean
    import ms

    if path is None:
        path = ms.askForSave(extensions=["csv"])
        if path is None:
            return None
    tab.storeCSV(path)

