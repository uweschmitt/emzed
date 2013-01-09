#encoding: utf-8

from libms.DataStructures.Table import Table

def toTable(colName, iterable,  fmt="", type_=None, title="", meta=None):
    return Table.toTable(colName, iterable, fmt, type_, title, meta)

toTable.__doc__ = Table.toTable.__doc__

def mergeTables(tables):
    """ merges tables. Eg:

        .. pycon::
           t1 = ms.toTable("a",[1,2])
           t2 = t1.copy()
           t1.addColumn("b", [3,4])
           t2.addColumn("b", [5,5])
           t3 = ms.mergeTables([t1, t2])
           t3.print_()

    """
    t0 = tables[0].buildEmptyClone()
    t0.append(tables)
    return t0

def openInBrowser(urlPath):
    """
    opens *urlPath* in browser, eg:

    .. pycon::
        ms.openInBrowser("http://emzed.biol.ethz.ch") !noexec

    """
    from PyQt4.QtGui import QDesktopServices
    from PyQt4.QtCore import QUrl
    import os.path

    url = QUrl(urlPath)
    scheme = url.scheme()
    if scheme not in ["http", "ftp", "mailto"]:
        # C:/ or something simiar:
        if os.path.splitdrive(urlPath)[0] != "":
            url = QUrl("file:///"+urlPath)
    ok = QDesktopServices.openUrl(url)
    if not ok:
        raise Exception("could not open '%s'" % url.toString())


def _recalculateMzPeakFor(postfix):
    def calculator(table, row, name, postfix=postfix):

        mzmin = table.get(row, "mzmin"+postfix)
        mzmax = table.get(row, "mzmax"+postfix)
        rtmin = table.get(row, "rtmin"+postfix)
        rtmax = table.get(row, "rtmax"+postfix)
        pm    = table.get(row, "peakmap"+postfix)
        mz = pm.representingMzPeak(mzmin, mzmax, rtmin, rtmax)
        return mz if mz is not None else (mzmin+mzmax)/2.0
    return calculator

def _hasRangeColumns(table, postfix):
    return all([table.hasColumn(n + postfix) for n in ["rtmin", "rtmax",
                                                 "mzmin", "mzmax", "peakmap"]])

def recalculateMzPeaks(table):
    #TODO: tests !
    """Adds mz value for peaks not detected with centwaves algorithm based on
       rt and mz window: needed are columns mzmin, mzmax, rtmin, rtmax and
       peakmap mz, postfixes are automaticaly taken into account"""
    postfixes = [ "" ] + [ "__%d" % i for i in range(len(table.colNames))]
    for postfix in postfixes:
        if _hasRangeColumns(table, postfix):
            mz_col = "mz" + postfix
            if table.hasColumn(mz_col):
                table.replaceColumn(mz_col, _recalculateMzPeakFor(postfix),
                                    format="%.5f", type_=float)
            else:
                table.addColumn(mz_col, _recalculateMzPeakFor(postfix),
                                format="%.5f", type_=float)

