import ms


def testIsotopeShiftTable():
    # at the time writing this test I had no exact number for
    # isotope probabilites at hand. so for testing I just
    # created a fictive distribution table, which is injected
    # into isotopeTable()
    probs = {
                   "C": { 0: 0.9, 1: 0.08, 2: 0.02 },
                   "H": { 0: 0.99, 1: 0.01 },
                   "N": { 0: 0.7, 1: 0.22, 2: 0.07 },
                   "O": { 0: 0.8, 1: 0.1, 2: 0.1 },
                   "P": { 0: 0.9, 1: 0.1},
                   "S": { 0: 0.6, 1: 0.3, 2: 0.1 },
            }
    t = ms.isotopeTable("C", probs=probs)
    assert len(t) == 3, len(t)
    values = t.p.values
    assert values == [ 0.9, 0.08, 0.02], values

    t = ms.isotopeTable("CHNOPS")
    assert len(t) == 8, len(t)

    assert abs(t.rows[0][1] - 0.2694) < 0.001

    # the algo is very accurate:
    assert abs(sum(t.p.values)-1.0) < 0.03
