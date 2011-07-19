
import sys
sys.path.insert(0, "..")
from pyOpenMS import *

def test_load():
    p = Param()
    p.load("test.ini")
    assert "hallo" == p.getStrValue("uwe:test")

def test_load_and_store():
    p = Param()
    p.load("test.ini")
    p.store("test2.ini")
    p2 = Param()
    p2.load("test2.ini")
    assert "hallo" == p2.getStrValue("uwe:test")
    
