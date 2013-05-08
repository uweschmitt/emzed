# -*- coding: utf-8 -*-
"""
Created on Tue May 07 11:55:43 2013

@author: uweschmi
"""


import os.path
import _winreg

here = os.path.dirname(os.path.abspath(__file__))

def getPathToPythonExe():
    try:
        k0 = _winreg.OpenKey(_winreg.HKEY_CLASSES_ROOT,
                             r"Python.File\Shell\open\command")
    except WindowsError:
        try:
            k0 = _winreg.OpenKey(_winreg.HKEY_CURRENT_USER,
                                r"Software\Classes\Python.File\Shell\open\command")
        except WindowsError:
            return None

    value = _winreg.QueryValue(k0, "").split(" ")[0].strip("'").strip('"')
    path = os.path.dirname(value)
    return path

path_to_python_exe = getPathToPythonExe()
print "path to python.exe is", path_to_python_exe
if path_to_python_exe is not None:
    os.chdir(path_to_python_exe)
os.system("python %s %s _asadmin_" % (os.path.join(here, "_installer.py"), here))
