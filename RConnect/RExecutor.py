
import _winreg, os, glob, tempfile, subprocess
from   os.path import dirname, abspath, join

# all installled libs will get to local folder
R_LIBS=join(dirname(abspath(__file__)), "libs")
os.environ["R_LIBS"] = R_LIBS
if not os.path.exists(R_LIBS):
    os.mkdir(R_LIBS)


from utils import TemporaryDirectoryWithBackup


class RExecutor(object):

    # RExecutor is a Singleton:
    _instance = None
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(RExecutor, cls).__new__(
                                cls, *args, **kwargs)
        return cls._instance

    def __init__(self):

        self.rHome = RExecutor.findRHome()
        LLL.debug("found R home at "+self.rHome)
        self.rExe  = RExecutor.findRExe(self.rHome)
        LLL.debug("found R.exe at "+self.rExe)

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
        assert self.run_command("q(status=4711);") == 4711

    def run_script(self, path):
        # hyphens are needed as pathes may contain spaces
        cmd = '"%s" --vanilla --silent < %s' % (self.rExe, path)
        print cmd
        hasIpython = False

        try:
            __IPYTHON__  # check if run from IPython
            hasIpython = True
        except:
            pass
        
        # for developping it is better to use os.system which opens a new window and
        # shows progress
        if 0 and hasIpython:
            print __IPYTHON__.getoutput(cmd)
            return None # how to get return status ?
        else:
            return os.system(cmd)

    def run_command(self, command, dir_=None):

        if dir_ is not None:

            fp = file(os.path.join(dir_, "script.R"), "w")
            print >> fp, command
            fp.close()
            return self.run_script(fp.name)

        else:

            with TemporaryDirectoryWithBackup() as td:

                fp = file(os.path.join(td, "script.R"), "w")
                print >> fp, command
                fp.close()
                return self.run_script(fp.name)
            


if __name__ == "__main__":
   RExecutor().test()

    
    
    
