

def loadPeakMap(path=None):
    """ loads mzXML, mzML and mzData files 

        If *path* is missing, a dialog for file selection is opened
        instead.
    """

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
    """ load pickled table

        If *path* is missing, a dialog for file selection is opened
        instead.
    """

    # local import in order to keep namespaces clean
    import ms
    from   libms.DataStructures.Table import Table

    if path is None:
        path = ms.askForSingleFile(extensions=["table"])
        if path is None:
            return None

    return Table.load(path)

def loadCSV(path=None, sep=";", **specialFormats):
    # local import in order to keep namespaces clean
    import ms
    import csv, os.path
    from   libms.DataStructures.Table import (Table, commonTypeOfColumn,\
                                              bestConvert, guessFormatFor)

    if path is None:
        path = ms.askForSingleFile(extensions=["csv"])
        if path is None:
            return None

    with open(path,"r") as fp:
        # remove clutter at right margin
        reader = csv.reader(fp, delimiter=sep)
        colNames = [n.strip().replace(" ","_") for n in reader.next()]
        rows = [ [bestConvert(c.strip()) for c in row] for row in reader]


    columns = [[row[i] for row in rows] for i in range(len(colNames))]
    types = [commonTypeOfColumn(col) for col in columns]

    #defaultFormats = {float: "%.2f", str: "%s", int: "%d"}
    formats = dict([(name, guessFormatFor(name,type_)) for (name, type_)\
                                                  in zip(colNames, types)])
    formats.update(specialFormats)

    formats = [formats[n] for n in colNames]

    title = os.path.basename(path)
    meta = dict(loaded_from=os.path.abspath(path))
    return Table(colNames, types, formats, rows, title, meta)
