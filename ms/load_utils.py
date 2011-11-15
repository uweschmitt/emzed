

def loadPeakMap(path=None):

    """ loads mzXML, mzML and mzData files """

    # local import in order to keep namespaces clean
    import ms
    from   pyOpenMS import MSExperiment, FileHandler
    from   libms.DataStructures import PeakMap

    if path is None:
        path = ms.askForSingleFile(extensions="mzML mzXML mzData".split())
        if path is None:
            return None


    experiment = MSExperiment()
    fh  = FileHandler()
    fh.loadExperiment(path, experiment)

    return PeakMap.fromMSExperiment(experiment)

def loadTable(path=None):
    """ load pickled table """

    # local import in order to keep namespaces clean
    import ms
    from   libms.DataStructures import Table

    if path is None:
        path = ms.askForSingleFile(extensions=["table"])
        if path is None:
            return None

    return Table.load(path)
