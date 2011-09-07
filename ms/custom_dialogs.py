
def __fileDialog(startAt=None, onlyDirectories=False, multipleFiles=True, extensions=None):

    import guidata
    from PyQt4.QtGui import QFileDialog
    from PyQt4.QtCore import Qt

    import os

    if startAt is None:
        startAt = os.getcwd()

    app = guidata.qapplication()
    di=QFileDialog(directory=startAt)

    if extensions is not None:
        filter_ = "(%s)" % " ".join( "*."+e for e in extensions)
        di.setNameFilter(filter_)

    if onlyDirectories:
        di.setFileMode(QFileDialog.DirectoryOnly)
    elif multipleFiles:
        di.setFileMode(QFileDialog.ExistingFiles)
    else:
        di.setFileMode(QFileDialog.ExistingFile)

    di.setWindowFlags(Qt.Window)
    di.activateWindow()
    di.raise_()
    if di.exec_():
        files= di.selectedFiles()
        res = [unicode(f) for f in files]
        if onlyDirectories:
            return res[0]
        elif multipleFiles:
            return res
        else:
            return res[0]

    return None


def askForDirectory(startAt=None):
    """ 
          asks for a single directory.

          you can provide a startup directory with parameter startAt.

          returns the path to the selected diretory as a string,
          or None if the user aborts the dialog.
    """
    return __fileDialog(startAt, onlyDirectories=True)

def askForSingleFile(startAt=None, extensions=None):

    """ 
          asks for a single file.

          you can provide a startup directory with parameter startAt.
          you can restrict the files to select by providing a list
          of extensions.
          eg
              askForSingleFile(extensions=["csv"])
          or
              askForSingleFile(extensions=["mzXML", "mxData"])

          returns the path of the selected file as a unicode string,
          or None if the user aborts the dialog.
    """
    return __fileDialog(startAt, multipleFiles=False, extensions=extensions)

def askForMultipleFiles(startAt=None, extensions=None):
    """ 
          asks for a single or multiple files.

          you can provide a startup directory with parameter startAt.
          you can restrict the files to select by providing a list
          of extensions.
          eg
              askForSingleFile(extensions=["csv"])
          or
              askForSingleFile(extensions=["mzXML", "mxData"])

          returns the pathes of the selected files as a list of unicode strings,
          or None if the user aborts the dialog.
    """
    return __fileDialog(startAt, multipleFiles=True, extensions=extensions)


def chooseConfig(configs, params):
    
    from libms.gui.ConfigChooseDialog import ConfigChooseDialog
    import guidata

    app = guidata.qapplication()
    dlg = ConfigChooseDialog(configs, params)
    dlg.activateWindow()
    dlg.raise_()
    dlg.exec_()

    return dlg.result


#def show(what):
    
#    import guidata
#    from   libms.gui.TableDialog import showTable
#    from   libms.DataStructures import Table
#    from   libms.pyOpenMS import PeakMap
#    from   libms.mzExplorer import inspectMap

#    if isinstance(what, Table):
#        showTable(what)

#    elif isinstance(what, PeakMap):
#        inspectMap(what)

#    else:
#        print "do not now how to show %r" % what
        

    
    
    

if __name__ == "__main__":

    #print askForDirectory()
    #print askForSingleFile()
    print askForMultipleFiles(extensions=["py", "pyc"])
    
