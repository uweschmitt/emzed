
import ms

import tempfile



def test_load():
    p = ms.loadParam("data/test.ini")
    assert "hallo" == p["uwe:test"]
    

    ms.saveParam(p, "temp_output/test.ini")
    p2 = ms.loadParam("temp_output/test.ini")
    assert "hallo" == p2["uwe:test"]

def test_all_types():
    p = dict()

    p["uwe:schmitt"] = "hi"
    p["uwe:schmitt:alter"] = 40
    p["uwe:schmitt:gewicht"] =99.2

    ms.saveParam(p, "temp_output/test.ini")
    p2 = ms.loadParam("temp_output/test.ini")

    assert p["uwe:schmitt"] == "hi"
    assert type(p["uwe:schmitt"] ) == str
    assert p["uwe:schmitt:alter"] == 40
    assert type(p["uwe:schmitt:alter"] ) == int
    assert p["uwe:schmitt:gewicht"] == 99.2
    assert type(p["uwe:schmitt:gewicht"]) == float
    
