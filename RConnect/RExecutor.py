
import _winreg, os, glob, tempfile, subprocess
from   os.path import dirname, abspath, join

# all installled libs will get to local folder
R_LIBS=join(dirname(abspath(__file__)), "libs")
os.environ["R_LIBS"] = R_LIBS
if not os.path.exists(R_LIBS):
    os.mkdir(R_LIBS)
    


class RExecutor(object):

    def __init__(self):

        self.rHome = RExecutor.findRHome()
        self.rExe  = RExecutor.findRExe(self.rHome)

    @staticmethod
    def findRHome():

        pathToR = None

        for finder in  [ lambda : RExecutor.path_from(_winreg.HKEY_CURRENT_USER),
                         lambda : RExecutor.path_from(_winreg.HKEY_LOCAL_MACHINE),
                         lambda : os.environ.get("R_HOME"),
                       ]:
            try:
                pathToR = finder()
                if pathToR != None:
                   break
            except (KeyError, WindowsError):
                pass 


        if pathToR is None:
            raise Exception("install dir of R not found, neither in registry, nor is R_HOME set.")
    
        return pathToR

    @staticmethod
    def findRExe(rHome):

        found = glob.glob("%s/bin/R.exe" % rHome)
        if found:
            return found[0]
        else:
            found = glob.glob("%s/bin/*/R.exe" % rHome)
            if not found:
                raise Exception("could not find R.exe")
            if len(found)>1:
                print "found multiple R.exe !"
                for p in found:
                    print "    ", p
                print "I will take the first one !"

            return found[0]
        

    @staticmethod
    def path_from(regsection):

        key = _winreg.OpenKey(regsection, "Software\\R-core\\R")
        return _winreg.QueryValueEx(key, "InstallPath")[0]

    


    def run_test(self):
        assert self.run_commands("q(status=4711);") == 4711


    def run_script(self, path):
        cmd = "%s --vanilla --silent < %s" % (self.rExe, path)
        hasIpython = False
        try:
            __IPYTHON__  # check if run from IPython
            hasIpython = True
        except:
            pass
        
        if hasIpython:
            print "run ", cmd
            print __IPYTHON__.getoutput(cmd)
        else:
            return os.system(cmd)

    
    def run_commands(self, command):

        fp = tempfile.NamedTemporaryFile(delete=False) 
        try:
            print >> fp, command
            fp.close()
            return self.run_script(fp.name)
        finally:
            os.remove(fp.name)
        


if __name__ == "__main__":
   RExecutor().test()

    
    
    
