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
    assert len(tn) >= 2709, len(tn)

def test_handling_of_wrong_answer_from_metlin():
    t = ms.loadCSV("data/metlin_input.csv")
    assert len(t) == 2, len(t)
    tn = ms.matchMetlin(t, "mass__0", ["M"], 3)
    assert len(tn) == 12, len(tn)
    assert set(tn.formula__1.values) == set(["C7H14O6", "C13H10N2"])

