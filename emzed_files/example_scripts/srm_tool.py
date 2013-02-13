# -*- coding: utf-8 -*-
"""
Created on Fri Nov 30 11:00:49 2012

@author: pkiefer

"""

import ms


def process_srm_data(peakmap, transitions, delta_mz):

    tables = split_srm_peakmap_by_precursors_to_tables(peakmap, delta_mz)
    # Each table in tables now contains chromatograms for each precursor

    # We flatten each of these tables to one row tables, so that
    # the table explorer overlays these chromatograms if you select
    # a specific row.
    if transitions is not None:
        tables = integrate_matching_fragments(tables, transitions, delta_mz)
    else:
        tables = integrate_fragments(tables)

    flattened_tables = [flatten(t) for t in tables]

    # Concatenate all these one row table to one big result table:
    merged = ms.mergeTables(flattened_tables)

    # For later visual inspection with the table explorer a title is helpful.
    # Here we use the name of the peakmap file:
    merged.title = "SRM peaks of %s" % peakmap.meta["source"]
    return merged


def split_srm_peakmap_by_precursors_to_tables(peakmap, delta_mz):
    """ split a srm/mrm peakmap to tables with  mass transitions, mz ranges and
    corresponding MS2 data peakmaps.

    the result tables have columns:
       - precursor (mz value, uniqued for each table),
       - fragment (mz value)
       - mzmin, mzmax (calculated as fragment +/- delta_mz)
       - peakmap.
    """
    measured_transitions = []

    ms2_maps = peakmap.splitLevelN(2)

    for pre_mz, ms2_map in ms2_maps:
        # get unique fragment ions in level 2 map in ascending order:
        ions = sorted(set(mz for mz, I in ms2_map.msNPeaks(2)))
        # build a  table with 'number of ions' rows
        table = ms.toTable("precursor", [pre_mz] * len(ions))
        table.addColumn("fragment", ions)
        table.addColumn("peakmap", ms2_map)
        table.addColumn("mzmin", table.fragment - delta_mz)
        table.addColumn("mzmax", table.fragment + delta_mz)
        measured_transitions.append(table)

    return measured_transitions

def integrate_matching_fragments(tables, transitions, delta_mz):
    """extracts mass transitions defined in transition table 'transitions'
    with column names 'name', 'precursor', 'fragment', 'rtmin', 'rtmax'.

    Detecting the peaks does not use a peak detector as centWave, but uses mz
    and rt ranges to fit a EMG model to the underlying raw peaks m/z traces.
    This avoids cumbersome parameter optimization of a peak detector and
    returns all peaks irrespective of filtering according to some heuristic
    criterion for peak quality.
    """

    table = ms.mergeTables(tables)
    # To shorten the name in commands we introduce abbreviations
    trans = transitions
    t = table

    # find candidates defined in parameter table transitions
    identified = t.join(trans,
                        trans.precursor.approxEqual(t.precursor, delta_mz)\
                        & trans.fragment.approxEqual(t.fragment, delta_mz))

    # identified.info() would show now:
    #
    # 0  [3 diff vals, 0 Nones]    name='precursor' ..
    # 1  [9 diff vals, 0 Nones]    name='fragment'  ..
    # 2  [3 diff vals, 0 Nones]    name='peakmap'  ..
    # 3  [9 diff vals, 0 Nones]    name='mzmin'  ..
    # 4  [9 diff vals, 0 Nones]    name='mzmax' ..
    # 5  [9 diff vals, 0 Nones]    name='name__0'  ..
    # 6  [9 diff vals, 0 Nones]    name='precursor__0'  ..
    # 7  [9 diff vals, 0 Nones]    name='fragment__0'  ..
    # 8  [9 diff vals, 0 Nones]    name='rtmin__0'  ..
    # 9  [9 diff vals, 0 Nones]    name='rtmax__0'  ..

    identified.renameColumns(name__0="name",
                             rtmin__0="rtmin",
                             rtmax__0="rtmax")

    identified = identified.extractColumns("name", "precursor", "fragment",
                                           "mzmin", "mzmax", "rtmin", "rtmax",
                                           "peakmap")

    # now we have columns mzmin, mzmax, rtmin, rtmax and peakmap which we
    # need for fitting EMG model with ms.integrate:
    identified = ms.integrate(identified, "emg_exact")
    return identified.splitBy("name")

def integrate_fragments(measured_transitions):
    """
    Fit a EMG model to each fragment. we use the full rt range as rt limits.
    As this model fits against the peak with maximal intensity, this approach
    is feasible for exploration.
    """
    result=[]
    for table in measured_transitions:
        # column peakmap has one unique value, take this to get values
        # for rtmin and rtmax:
        rtmin, rtmax = table.peakmap.uniqueValue().rtRange()
        table.addColumn("rtmin", rtmin)
        table.addColumn("rtmax", rtmax)

        # Now table has columns rtmin/rtmax, mzmin/mzmax and peakmap. These are
        # mandatory for fitting EMG model with ms.integrate:
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
        """ SRM Tool
        This tool allows exploration and targeted extraction of SRM
        data. You can choose the mode of operation below. In case
        you choose "explore", the field "parameter table" is obsolete.

        For targeted extraction, the parameter table is a csv file
        with columns name, fragment, precursor, rtmin and rtmax.
        """
        delta_mz = gui.FloatItem("m/z half isolation width\nof precursor [Da]",
                                default=0.5)
        mode=gui.ChoiceItem("mode of operation",
                        ["explore", "targeted extraction"],
                        default=1,
                        help="for explore mode no parameter table is needed")
        path_para  =gui.FileOpenItem("parameter table", ("csv"))
        path_data = gui.FileOpenItem("data file to process",
                                                   ("mzXML", "mzML", "mzData"))

    frontend = SRMExplorer()
    exit_code = frontend.show()

    if exit_code == 1:     # means: ok button pressed

        print "LOAD DATA"
        peakmap = ms.loadPeakMap(frontend.path_data)

        if frontend.mode == 1:
            transitions = ms.loadCSV(frontend.path_para)
            # Edit parameter table
            required_columns=["name", "fragment", "precursor",
                              "rtmin", "rtmax"]
            assert transitions.hasColumns(*required_columns),\
                    "Please check column names in parameter table !!"
            transitions.title="SRM parameter table"
        else:
            transitions = None

        print "PROCESS DATA"
        result = process_srm_data(peakmap, transitions, frontend.delta_mz)
        ms.inspect(result)
