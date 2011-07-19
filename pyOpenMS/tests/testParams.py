
import sys
sys.path.insert(0, "..")
from pyOpenMS import *

def test_load():
    p = paramFromFile("tests/data/test.ini")
    assert "hallo" == p.getStrValue("uwe:test")

def test_load_and_store():
    p = paramFromFile("tests/data/test.ini")
    p.store("tests/test2.ini")
    p2 = paramFromFile("tests/test2.ini")
    assert "hallo" == p2.getStrValue("uwe:test")
    
