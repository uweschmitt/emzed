#encoding: utf-8

import installConstants as _installConstants # installx MMU

def mzalign(table, fullC13=False, tol=15*MMU, universal_metabolites=None,
            destination=None, minR2=0.95, minPoints=5, interactive=False):

    import ms
    import tab
    import os
    import numpy as np
    import mzalign_helpers
    from mzalign_helpers import (_buildHypotheseTable,
                                 _findMzMatches,
                                 _findParametersAutomatically,
                                 _findParametersManually,
                                 _plotAndSaveMatch,
                                 _applyTransform )

    if not interactive:
        assert minR2 <= 1.0
        assert minPoints > 1

    sources = set(table.source.values)
    assert len(sources) == 1
    source = sources.pop()

    if universal_metabolites is None:
        universal_metabolites = tab.universal_metabolites
    univ = universal_metabolites
    univ.requireColumn("m0")
    univ.requireColumn("rtmin")
    univ.requireColumn("rtmax")
    univ.requireColumn("mf")
    assert univ.get(univ.colTypes, "m0") == float,\
        "col m0 is not float"
    assert univ.get(univ.colTypes, "rtmin") == float,\
        "col rtmin is not float"
    assert univ.get(univ.colTypes, "rtmax") == float,\
        "col rtmax is not float"

    polarities = set(table.polarity.values)
    assert len(polarities) == 1, "multiple polarities in table"
    polarity = polarities.pop()

    hypot = _buildHypotheseTable(polarity, univ.copy(), fullC13)

    if destination is not None:
        basename = os.path.basename(source)
        fname, _ = os.path.splitext(basename)
        hypot.store(os.path.join(destination, fname+"_hypot.table"), True)

    real, tobe, matches = _findMzMatches(hypot, table, tol)
    if len(real)<=1:
        print "NOT ENOUGH MATCHES"
        return

    if interactive:
        ms.inspect(matches)

    elif len(tobe) < minPoints:
        raise Exception("could only match %d peaks" % len(tobe))

    if not interactive:
        transform, used = _findParametersAutomatically(tobe.copy(), real.copy(),\
                                                      minR2, minPoints)
    else:
        transform, used = _findParametersManually(tobe.copy(), real.copy())
        if transform is None:
            print "ABORTED"
            return

    if destination is not None:
        matches.addColumn("error", np.linalg.norm(transform(real)-tobe), float,\
                          "%.3e")
        matches.store(os.path.join(destination, fname+"_mzalign.table"), True)
        matches.storeCSV(os.path.join(destination, fname+"_mzalign.csv"))

        path = os.path.join(destination, fname+"_mzalign.png")
        _plotAndSaveMatch(tobe, real, used, transform, path)

    _applyTransform(table, transform)
    print "DONE"
