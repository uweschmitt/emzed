import _winreg
import os
import ConfigParser

class GlobalConfig(object):

    def __init__(self):
        key =_winreg.OpenKey(_winreg.HKEY_CURRENT_USER,
                            "Software\\Microsoft\\Windows\\CurrentVersion"
                            "\\Explorer\\User Shell Folders")

        appRoot,_ = _winreg.QueryValueEx(key, "AppData")
        appRoot = _winreg.ExpandEnvironmentStrings(appRoot)
        appFolder = os.path.join(appRoot, "mzExplore")
        if not os.path.exists(appFolder):
            os.makedirs(appFolder)
        self.configFilePath=os.path.join(appFolder, "global.ini")
        if not os.path.exists(self.configFilePath):
            self.editConfig()
            self.saveConfig()
        else:
            p = ConfigParser.ConfigParser()
            p.readfp(open(self.configFilePath))
            self.exchangeFolder = p.get("DEFAULT", "exchange_folder")

    def getExchangeFolder(self):
        return self.exchangeFolder

    def editConfig(self):
        import guidata
        app = guidata.qapplication()
        import guidata.dataset.datatypes as dt
        import guidata.dataset.dataitems as di
        class ConfigEditor(dt.DataSet):
            """ ConfigEditor

                Please provide a global exchange folder for databases,
                scripts and configs shared among your lab.

                If you work only locally, you can abort this dialog.
            """
            exchangeFolder = di.DirectoryItem("Global exchange folder:")

        dlg = ConfigEditor()
        dlg.edit()
        self.exchangeFolder = dlg.exchangeFolder

    def saveConfig(self):
        p = ConfigParser.ConfigParser()
        p.set("DEFAULT", "exchange_folder", self.exchangeFolder)
        p.write(open(self.configFilePath, "w"))



def getDocumentFolder():
    key =_winreg.OpenKey(_winreg.HKEY_CURRENT_USER,
                        "Software\\Microsoft\\Windows\\CurrentVersion"
                        "\\Explorer\\User Shell Folders")
    personalRoot,_ = _winreg.QueryValueEx(key, "Personal")
    return _winreg.ExpandEnvironmentStrings(personalRoot)

def getDataHome():
    dataHome = os.path.join(getDocumentFolder(), "mzExplore")
    if not os.path.exists(dataHome):
        os.makedirs(dataHome)
    return dataHome

def getExchangeFolder():
    folder = GlobalConfig().getExchangeFolder()
    if folder is not None:
        return folder
    exchangeFolder = os.path.join(getDataHome(), "shared")
    if not os.path.exists(exchangeFolder):
        os.makedirs(exchangeFolder)
    return exchangeFolder




