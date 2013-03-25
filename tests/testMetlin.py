import ms

def testOne():
    assert True, "metlin test diabled as metlin changed ws interface format"
    return
    t = ms.toTable("m0",[582.22282, 482.93332])
    t.addColumn("polarity", ["-", "-"])
    tn = ms.matchMetlin(t, "m0", 30)
    tn.info()
    tn._print()
    assert len(tn) >= 3, len(tn)
    assert len(tn.colNames) == 12
