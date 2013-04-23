# -*- coding: utf-8 -*-
"""
Created on Fri Nov 30 11:00:49 2012

@author: pkiefer

"""

import ms


def process_srm_data(peakmap, n_digits):

    tables = split_srm_peakmap_to_tables(peakmap, n_digits)
    # Each table in tables now contains chromatograms for each precursor

    # We flatten each of these tables to one row tables, so that
    # the table explorer overlays these chromatograms if you select
    # a specific row.
    flattened_tables = [flatten(t) for t in tables]

    # Concatenate all these one row table to one big result table:
    merged =  ms.mergeTables(flattened_tables)

    # For later visual inspection with the table explorer a title is helpful.
    # Here we use the name of the peakmap file:
    merged.title = "SRM/MRM analysis of %s" % peakmap.meta["source"]
    return merged


def split_srm_peakmap_to_tables(peakmap, n_digits=2):
    """ Processes a srm/mrm peakmap.
    The result is a list of tables with chromatographic peaks of MS2 data. The
    peaks are integrated over the full time range of the individual MS2
    peakmaps.

    n_digits is the precision of the precursor m/z values.

    Detecting the peaks does not use a peak detector as centWave, but uses
    mz ranges to fit a EMG model to the underlying raw peaks m/z traces. This avoids
    cumbersome parameter optimization of a peak detector and returns all peaks
    irrespective of filtering according to some heuristic criterion for peak
    quality.
    """

    result = []
    ms2_maps = peakmap.splitLevelN(2, n_digits)

    # half resolution according to n_digits:
    delta_mz = 0.5 * (0.1)**n_digits

    for pre_mz, ms2_map in ms2_maps:

        # get unique m/z values in level 2 map in ascending order:
        ions = sorted(set(mz for mz, I in ms2_map.msNPeaks(2)))

        # build a  table with 'number of ions' rows
        table = ms.toTable("precursor", [pre_mz] * len(ions))
        table.addColumn("fragment_ion", ions)

        # Set rt range for later integration. We do no specific peak detection
        # here but use the full time range:
        rtmin, rtmax = ms2_map.rtRange()
        table.addColumn("rtmin", rtmin)
        table.addColumn("rtmax", rtmax)
        table.addColumn("mzmin", table.fragment_ion - delta_mz)
        table.addColumn("mzmax", table.fragment_ion + delta_mz)
        table.addColumn("peakmap", ms2_map)

        # Now rtmin/rtmax, mzmin/mzmax and peakmap columns are created. These
        # are mandatory for fitting and integrating peaks with ms.integrate:
        table = ms.integrate(table, "emg_exact")
        result.append(table)

    return result


def flatten(table):
    """
    Merges all rows of a table vertically, so a table with n rows
    and m columns is converted to a table with one row and m*n columns.

    The origin of the columns are indicated by postfixes "__i", where
    i starts with zero and is the index of underlying row.

    So if we have a input table

        a     b
        ----- -----
        0     1
        2     3

    the flattened table is

        a__0  b__0  a__1  b__1
        ----- ----  ----- -----
        0     1     2     3
    """

    # We rename columns for wanted naming scheme, without this modification,
    # the example result above would have column names [ "a", "b", "a__0",
    # "b__0"]
    # This is caused by the way leftJoin creates column names for the result.

    if len(table) == 0:
        add_postfix_to_column_names(table, "__0")
        return table

    # tables support indexing for building subtables:
    # (using slices, as table[1:-1] or table[::2] works too !)
    result = table[0]
    add_postfix_to_column_names(result, "__0")

    # here we build the result:
    for i in range(1, len(table)):
        result = result.leftJoin(table[i])
    return result


def add_postfix_to_column_names(table, postfix):
    mapping = dict((name, name + postfix) for name in table.colNames)
    table.renameColumns(mapping)


if __name__ == "__main__":

    import libms.gui.DialogBuilder as gui

    class SRMExplorer(gui.WorkflowFrontend):
        n_digits = gui.IntItem("no of significant digits\nof precursor m/z",
                                default=2)
        path = gui.FileOpenItem("data file to process",
                                ("mzXML", "mzML", "mzData"))


    frontend = SRMExplorer()
    exit_code = frontend.show()
    if exit_code:
        print "LOAD DATA"
        peakmap = ms.loadPeakMap(frontend.path)
        print "PROCESS DATA"
        result = process_srm_data(peakmap, frontend.n_digits)
        ms.inspect(result)
