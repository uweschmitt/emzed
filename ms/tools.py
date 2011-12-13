from libms.DataStructures.Table import Table

def toTable(colName, iterable,  fmt=None, type_=None, title="", meta=None):
    return Table.toTable(colName, iterable, fmt, type_, title, meta)

toTable.__doc__ = Table.toTable.__doc__

def mergeTables(tables):
    t0 = tables[0].buildEmptyClone()
    t0.append(tables)
    return t0
