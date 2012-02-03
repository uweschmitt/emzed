from Tkinter import *
import tkFileDialog
import _winreg

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

        import os
        programFolder = os.environ.get("PROGRAMFILES")
        # folgendes konfigurierbar machen:
        if os.access(programFolder, os.W_OK):
            defaultDir = os.path.join(programFolder, "emzed", "emzed_1.0")
        else:
            key =_winreg.OpenKey(_winreg.HKEY_CURRENT_USER,
                                "Software\\Microsoft\\Windows\\CurrentVersion"
                                "\\Explorer\\User Shell Folders")
            personalRoot,_ = _winreg.QueryValueEx(key, "Personal")
            defaultDir =  os.path.join(_winreg.ExpandEnvironmentStrings(personalRoot), "emzed", "emzed_1.0")

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


