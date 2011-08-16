
import _winreg, os

def path_from(kk):

    key = _winreg.OpenKey(kk, "Software\\R-core\\R")
    return _winreg.QueryValueEx(key, "InstallPath")[0]

path = None

try:
    path = path_from(_winreg.HKEY_CURRENT_USER)
    if path==None: 
        path = path_from(_winreg.HKEY_LOCAL_MACHINE)
except WindowsError:
    pass

if path==None: 
    path=os.environ["R_HOME"]
   
import glob

found = glob.glob("%s/bin/R.exe" % path)
if found:
    full_path_to_exe = found[0]
else:
    found = glob.glob("%s/bin/*/R.exe" % path)
    if not found:
        raise Exception("could not find R.exe")
    if len(found)>1:
        print "found multiple R.exe !"
        for p in found:
            print "    ", p
        print "I will take the first one !"

    full_path_to_exe = found[0]


script_path="test.r"
os.system("%s --vanilla < %s" % (full_path_to_exe, script_path))


    
    
    
