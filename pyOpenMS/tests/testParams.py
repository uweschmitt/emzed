
import sys, os
sys.path.insert(0, "..")
from pyOpenMS import *

class tempFileName(object):

    """ automatically deletes file when leaving the context 
        such that temporary files do not clutter the directory,
        eg if you are using a VCS. """
   
    def __init__(self, name):
        self.name = name

    def __enter__(self):
        return self.name

    def __exit__(self, *a):
        pass #os.remove(self.name)



def test_load():
    p = paramFromFile("tests/data/test.ini")
    assert "hallo" == p.getStrValue("uwe:test")

def test_load_and_store():
    p = paramFromFile("tests/data/test.ini")
    with tempFileName("tests/test2.ini") as name:
        p.store(name)
        p2 = paramFromFile(name)
    assert "hallo" == p2.getStrValue("uwe:test")

def test_all_types():
    p = Param()
    p.setStrValue("uwe:schmitt", "hi")
    p.setIntValue("uwe:schmitt:alter", 40)
    p.setFloatValue("uwe:schmitt:gewicht", 99.2)

    assert p.getStrValue("uwe:schmitt") == "hi"
    assert p.getIntValue("uwe:schmitt:alter") == 40
    assert p.getFloatValue("uwe:schmitt:gewicht") == 99.2

    with tempFileName("tests/uwe_schmitt.ini") as name:
        p.store(name)
        p = paramFromFile(name)

    assert p.getStrValue("uwe:schmitt") == "hi"
    assert p.getIntValue("uwe:schmitt:alter") == 40
    assert p.getFloatValue("uwe:schmitt:gewicht") == 99.2
    
