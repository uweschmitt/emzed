# -*- coding: utf-8 -*-
"""
Created on Fri Nov 30 11:00:49 2012

@author: pkiefer

"""

import ms

def _fragmentOverlay(compound_table, pstfx="__0"):
    """
    """

    assert len(compound_table), "can not handle empty table"

    ions = compound_table.splitBy("fragment_ion")
    assert all(len(ion) == 1 for ion in ions)

    #rename columns for nicer naming scheme:
    mapping = dict((name, name+pstfx) for name in ions[0].colNames)
    ions[0].renameColumns(mapping)

    ions = compound_table.splitBy("fragment_ion")
    assert all(len(ion) == 1 for ion in ions)

    # we build a flat one row table from a list of one row tables by
    # horizontally appending the columns:
    result = ions[0]
    for ion in ions[1:]:
        result = result.leftJoin(ion)
    return result

def split_srm_peakmap_to_tables(peakmap):

    result = []

    ms2_maps = peakmap.splitLevelN(2, 2) # level 2, 2 digits precursor presc
    for pre_mz, ms2_map in ms2_maps[:3]:

        ions = sorted(set(mz for mz, I in ms2_map.msNPeaks(2)))

        table = ms.toTable("precursor", [pre_mz] * len(ions))
        table.addColumn("fragment_ion", ions)

        rtmin, rtmax = ms2_map.rtRange()
        table.addColumn("rtmin", rtmin)
        table.addColumn("rtmax", rtmax)

        table.addColumn("mzmin", table.fragment_ion - 0.05)
        table.addColumn("mzmax", table.fragment_ion + 0.05)

        table.addColumn("peakmap", ms2_map)

        table = ms.integrate(table, "emg_exact")
        table.title = "%.2f" % pre_mz

        flattened = _fragmentOverlay(table)
        result.append(flattened)

    return result

if __name__ == "__main__":

    import sys
    fname, = sys.argv[1:]
    peakmap=ms.loadPeakMap(fname)
    result= split_srm_peakmap_to_tables(peakmap)
    result = ms.mergeTables(result)
    ms.inspect(result)



