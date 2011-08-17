
import _winreg, os, glob, tempfile


class RExecutor(object):

    def __init__(self):

        pathToR = None

        for finder in  [ lambda : RExecutor.path_from(_winreg.HKEY_CURRENT_USER),
                         lambda : RExecutor.path_from(_winreg.HKEY_LOCAL_MACHINE),
                         lambda : os.environ["R_HOME"],
                       ]:
            try:
                pathToR = finder()
                break
            except (KeyError, WindowsError):
                pass 


        if pathToR is None:
            raise Exception("install dir of R not found, neither in registry, nor is R_HOME set.")


        found = glob.glob("%s/bin/R.exe" % pathToR)
        if found:
            self.path_to_exe = found[0]
        else:
            found = glob.glob("%s/bin/*/R.exe" % path)
            if not found:
                raise Exception("could not find R.exe")
            if len(found)>1:
                print "found multiple R.exe !"
                for p in found:
                    print "    ", p
                print "I will take the first one !"

            self.path_to_exe = found[0]
        

    @staticmethod
    def path_from(regsection):

        key = _winreg.OpenKey(regsection, "Software\\R-core\\R")
        return _winreg.QueryValueEx(key, "InstallPath")[0]


    def run_test(self):
        assert self.run_commands("q(status=4711);") == 4711


    def run_script(self, path):
        return os.system("%s --vanilla < %s" % (self.path_to_exe, path))

    
    def run_commands(self, *commands):

        fp = tempfile.NamedTemporaryFile(delete=False) 
        try:
            for command in commands:
                print >> fp, command

            fp.close()

            return self.run_script(fp.name)
        finally:
            os.remove(fp.name)
        


if __name__ == "__main__":
   RExecutor().test()

    
    
    
