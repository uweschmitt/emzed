import ms

def test_small():

    t = ms.toTable("m0",[195.0877, 194.07904])
    tn = ms.matchMetlin(t, "m0", ["M"], 30)
    assert len(tn) == 23
    assert len(set(tn.formula__0.values)) == 5
    t = ms.toTable("m0",[195.0877, ])
    tn = ms.matchMetlin(t, "m0", ["M", "M+H"], 30)
    assert len(tn) == 23
    assert len(set(tn.formula__0.values)) == 5

def test_large():
    import time
    mz_values = [185.0877 + i for i in range(500)]
    t = ms.toTable("m0", mz_values)
    start = time.time()
    tn = ms.matchMetlin(t, "m0", ["M"], 30)
    assert len(tn) >= 3057
