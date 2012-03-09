import _winreg
import os, shutil
import ConfigParser

class _GlobalConfig(object):

    def __init__(self):
        key =_winreg.OpenKey(_winreg.HKEY_CURRENT_USER,
                            "Software\\Microsoft\\Windows\\CurrentVersion"
                            "\\Explorer\\User Shell Folders")

        appRoot,_ = _winreg.QueryValueEx(key, "AppData")
        appRoot = _winreg.ExpandEnvironmentStrings(appRoot)
        appFolder = os.path.join(appRoot, "emzed")
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

        def check_value(self, value):
            if not isinstance(value, self.type):
                return False
            if str(value).strip()=="":
                return True
            return di.DirectoryItem._check_value(self, value)

        di.DirectoryItem._check_value = di.DirectoryItem.check_value
        di.DirectoryItem.check_value = check_value
        class ConfigEditor(dt.DataSet):
            """ ConfigEditor

                Please provide a global exchange folder for databases,
                scripts and configs shared among your lab.

                If you do not have such an exchange folder, just click 'Ok'.
            """
            exchangeFolder = di.DirectoryItem("Global exchange folder:", notempty=False)

        dlg = ConfigEditor()
        dlg.edit()
        self.exchangeFolder = dlg.exchangeFolder
        di.DirectoryItem.check_value = di.DirectoryItem._check_value

    def saveConfig(self):
        p = ConfigParser.ConfigParser()
        p.set("DEFAULT", "exchange_folder", self.exchangeFolder or "")
        p.write(open(self.configFilePath, "w"))



def getDocumentFolder():
    key =_winreg.OpenKey(_winreg.HKEY_CURRENT_USER,
                        "Software\\Microsoft\\Windows\\CurrentVersion"
                        "\\Explorer\\User Shell Folders")
    personalRoot,_ = _winreg.QueryValueEx(key, "Personal")
    return _winreg.ExpandEnvironmentStrings(personalRoot)

def getDataHome():
    dataHome = os.path.join(getDocumentFolder(), "emzed_files")
    return dataHome

def getExchangeFolder():
    folder = _GlobalConfig().getExchangeFolder()
    if folder:
        return folder
    # no global exchange folder set, use local folder instead:
    exchangeFolder = os.path.join(getDataHome(), "shared")
    if not os.path.exists(exchangeFolder):
        os.makedirs(exchangeFolder)
    return exchangeFolder




