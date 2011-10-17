

def loadExperiment(path=None):

    """ loads mzXML, mzML and mzData files """

    # local import in order to keep namespaces clean
    import os.path
    import ms
    from   pyOpenMS import String, DataValue, MSExperiment, FileHandler

    if path is None:
        path = ms.askForSingleFile(extensions="mzML mzXML mzData".split())
        if path is None:
            return None


    experiment = MSExperiment()
    fh  = FileHandler()
    fh.loadExperiment(path, experiment)
    experiment.setMetaValue(String("source"), DataValue(os.path.basename(path)))
    #experiment.meta["source"] = os.path.basename(source) # for nicer display
    
    return experiment
