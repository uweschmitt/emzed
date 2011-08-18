from tempfile import mkdtemp
from shutil   import rmtree, copytree

class TemporaryDirectoryWithBackup(object):

    def __init__(self, keep=False):
        self.keep = keep

    def __enter__(self):
        self.d = mkdtemp()
        return self.d

    def __exit__(self, a, b, c):

        rmtree("last_temp_dict", ignore_errors = True) # might not exist
        copytree(self.d, "last_temp_dict")
        
        if not self.keep:
            rmtree(self.d) 
        
