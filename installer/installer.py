from Tkinter import *
import tkFileDialog, tkMessageBox
import _winreg
import os

from win32com.client import Dispatch


def getLocalUserShellFolders():
    return _winreg.OpenKey(_winreg.HKEY_CURRENT_USER,
                           "Software\\Microsoft\\Windows\\CurrentVersion"
                           "\\Explorer\\User Shell Folders")

def getLocalMachineShellFolders():
    return _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE,
                           "Software\\Microsoft\\Windows\\CurrentVersion"
                           "\\Explorer\\User Shell Folders")
    return key

def expandVars(valueEx, **kw):
    saved = dict ( (k, os.environ.get(k)) for k in kw.keys())
    os.environ.update(kw)
    result = os.path.expandvars(valueEx)
    os.environ.update(saved)
    return result

def getLocalShellVar(name):
    return _winreg.QueryValueEx(getLocalUserShellFolders(), name)[0]

def getLocalMachineShellVar(name):
    return _winreg.QueryValueEx(getLocalMachineShellFolders(), name)[0]

def getPersonalRoot():
    return expandVars(getLocalShellVar("Personal"))

def getPersonalDesktop():
    return expandVars(getLocalShellVar("Desktop"))

def getPersonalPrograms():
    return expandVars(getLocalShellVar("Programs"))


def getCommonDesktop():
    return expandVars(getLocalMachineShellVar("Common Desktop"))

def getCommonPrograms():
    return expandVars(getLocalMachineShellVar("Common Programs"))


class App(object):

    def __init__(self, root):

        frame = Frame(root)
        frame.pack()
        self.frame = frame

        def set_grid(widget, r, c, **kw):
            default = dict(padx = 5, pady = 5, row=r, column=c)
            default.update(kw)
            getattr(widget, "grid").__call__(**default)

        sb = Scrollbar(frame)
        sb.pack(side=LEFT, fill=Y)
        set_grid(sb, 0, 5, sticky=N+S, padx=0)
        #sb.grid(row=0, column=5, sticky=N+S, padx = 5, pady = 5)

        t=Text(frame, wrap=WORD, bd= 0, yscrollcommand=sb.set, padx=15)
        txt = open("License.txt").read()
        t.insert(INSERT, txt)
        t.config(state=DISABLED)
        sb.config(command=t.yview)

        set_grid(t, 0, 0, sticky=N+S+E+W, columnspan=5, padx=5)

        self.checked = IntVar()
        c = Checkbutton(frame, text="I read and accept the license", variable=self.checked, command=self.licenceCheck)
        set_grid(c, 1, 1, sticky=W)

        l = Label(frame, text = "Install to:", width=10)
        set_grid(l, 2,0, sticky=E)
        self.path = Entry(frame, width=80)

        programFolder = os.environ.get("PROGRAMFILES")
        # folgendes konfigurierbar machen:
        if os.access(programFolder, os.W_OK):
            defaultDir = os.path.join(programFolder, "emzed", "emzed_1.0")
        else:
            personalRoot = getPersonalRoot()
            defaultDir =  os.path.join(personalRoot, "emzed", "emzed_1.0")

        self.path.insert(0, defaultDir)
        set_grid(self.path, 2,1, columnspan = 2)

        self.dirbutton = Button(frame, text="choose Destination", command=self.file_dialog)
        set_grid(self.dirbutton, 2, 3)

        b = Button(frame, text="Abort", command=self.abort, width=30, height=2)
        set_grid(b, 3, 1, sticky=W)

        self.okbutton = Button(frame, text="Install", command=self.install, width=30, height=2)
        set_grid(self.okbutton, 3, 2, sticky=E)

        self.licenceCheck()

    def abort(self):
        self.targetDir = None
        self.frame.quit()

    def install(self):
        self.targetDir = self.path.get()
        try:
            testPath = os.path.join(self.targetDir, "TESTPATH")
            try:
                # cleanup from leftoverso of other installs
                os.removedirs(testPath)
            except:
                pass
            os.makedirs(testPath)
            testFile = os.path.join(self.targetDir, "TEST")
            try:
                # cleanup from leftoverso of other installs
                os.remove(testFile)
            except:
                pass
            open(testFile, "w").write("42")
            os.remove(testFile)
        except BaseException, e:
            tkMessageBox.showwarning("Target", str(e))
        else:
            self.frame.quit()

    def file_dialog(self):
        dirname=tkFileDialog.askdirectory()
        self.path.delete(0,END)
        self.path.insert(0, dirname)

    def licenceCheck(self):
        state = NORMAL if self.checked.get() else DISABLED
        self.okbutton.config(state=state)
        self.dirbutton.config(state=state)
        self.path.config(state=state)


import sys
assert sys.platform.startswith("win")

root = Tk()
app = App(root)
root.mainloop()

if app.targetDir is None:
    exit()

import zipfile

f = zipfile.ZipFile("emzed_files.zip")
f.extractall(app.targetDir)


def createLink(path, name):
    shell = Dispatch("WScript.Shell")
    link = shell.CreateShortCut(os.path.join(path, name))
    link.Targetpath = os.path.join(app.targetDir, "emzed.pyw")
    link.WorkingDirectory = app.targetDir
    location =  os.path.abspath(os.path.join(app.targetDir, "emzed.ico"))
    # have to do that, do not know why, but else the icons are not
    # associated !!!
    location = location.replace(os.environ.get("PROGRAMFILES"), "%PROGRAMFILES%")
    link.IconLocation = location
    link.save()


try:
    createLink(getCommonDesktop(), "emzed 1.0.lnk")
    createLink(getCommonPrograms(), "emzed 1.0.lnk")
except:
    createLink(getPersonalDesktop(), "emzed 1.0.lnk")
    createLink(getPersonalPrograms(), "emzed 1.0.lnk")





