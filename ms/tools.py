
def toTable(iterable, colName, fmt=None, type_=None, title="", meta=None):
    from libms.DataStructures.Table import (commonTypeOfColumn,
                                            standardFormats, Table)
    values = list(iterable)
    if type_ is None:
        type_ = commonTypeOfColumn(values)
    if fmt is None:
        fmt = standardFormats.get(type_, "%r")
    if meta is None:
        meta = dict()
    rows = [[v] for v in values]
    return Table([colName], [type_], [fmt], rows, title, meta)

