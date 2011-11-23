
def toTable(iterable, colName, fmt=None, type_=None, title="", meta=None):
    """ generates a one-column table from an iterable, eg from a list,
        colName is name for the column.

        - if type_ is not given a common type for all values is determined,
        - if fmt is not given, a default format for type_ is used.

        further one can provide a title and meta data
    """

    from libms.DataStructures.Table import (commonTypeOfColumn,
                                            standardFormats, Table)
    values = list(iterable)
    if type_ is None:
        type_ = commonTypeOfColumn(values)
    if fmt is None:
        fmt = standardFormats.get(type_, "%r")
    if meta is None:
        meta = dict()
    else:
        meta = meta.copy()
    rows = [[v] for v in values]
    return Table([colName], [type_], [fmt], rows, title, meta)

