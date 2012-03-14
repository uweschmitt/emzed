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
