import pdb
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 30 11:00:49 2012

@author: pkiefer

"""
def enhancedMergeTables(tables, ref_table):
    """ merges a list of tables selecting column names of refTable
        and extracting those columns from each table in tables prior
        to merging. Missing columns are added filled with None values.
    """
    ref_columns=set(ref_table.colNames)
    table_list=[]
    for table in tables:
        comp_col=ref_columns.difference(set(table.colNames))
        if comp_col:
            for colname in comp_col:
                table.addColumn(colname, None, format=ref_table.getFormat(colname))
        tt=table.extractColumns(*ref_table.colNames)
        for colname in ref_table.colNames:
            tt.set(tt.colTypes, colname, ref_table.get(ref_table.colTypes, colname))
        table_list.append(tt)
    return ms.mergeTables(table_list)

def _fragmentOverlay(compound_table, pstfx="__0"):
    """
    """
    extracted_columns=["fragment_ion", "rtmin", "rtmax",  "mzmin", "mzmax",
                      "method", "area", "rmse", "peakmap",
                      "params"]
    ions=compound_table.splitBy("fragment_ion")
    assert len(ions)>1, "not enough elements in list"
    t1=ions[0]
    #rename columns
    for name in extracted_columns:
        col_0=name+pstfx
        t1.renameColumns(**{name:col_0})
    t2=ions[1].extractColumns(*extracted_columns)
    tt=t1.leftJoin(t2, True)
    for i in range(2, len(ions)):
          t2=ions[i].extractColumns(*extracted_columns)
          tt=tt.leftJoin(t2, True)
    return tt

def split_srm_peakmap_to_tables(peakmap):

    result = []

    ms2_maps = peakmap.splitLevelN(2, 2) # level 2, 2 digits precursor presc
    for pre_mz, ms2_map in ms2_maps:

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

        result.append(table)

        #table.addColumn("precursor", pre_mz, format="%.2f", insertBefore="fragment_ion")
        #table.addColumn("rtmin", ms2_map.allRts()[0], format="'%.2fm' %(o/60.0)")
        #table.addColumn("rtmax", ms2_map.allRts()[-1], format="'%.2fm' %(o/60.0)")
        #table.addColumn("mzmin",table.fragment_ion-0.05, format="%.2f")
        #table.addColumn("mzmax",table.fragment_ion+0.05, format="%.2f")
        #table.addColumn("peakmap", pm)
    #table_len=[len(t)for t in precursor_tables]
    #ref_table=precursor_tables[table_len.index(max(table_len))]
    #srm_data_set=enhancedMergeTables(precursor_tables,ref_table)
    #srm_data_set.title="srm_data_set"
    #return srm_data_set
    return result

import ms
if __name__ == "__main__":

    peakmap=ms.loadPeakMap("nselevse_H120529_410.mzXML")
    result= split_srm_peakmap_to_tables(peakmap)
    ms.inspect(result)



