#encoding: utf-8


def matchMetlin(table, massColumn, adducts, ppm):
    table.requireColumn(massColumn)
    from libms.WebserviceClients.Metlin import MetlinMatcher

    masses = [ "%.6f" % m for m in table.getColumn(massColumn).values ]

    internalRefColumn = "__metlin_massmatch"
    if table.hasColumn(internalRefColumn):
        table.dropColumns(internalRefColumn)
    table.addColumn(internalRefColumn, masses)

    try:
        metlinMatch = MetlinMatcher.query(masses, adducts, ppm)
        if metlinMatch is None:
            table.addColumn("molid", None)
            table.dropColumns(internalRefColumn)
            return table

        result = table.leftJoin(metlinMatch, table.getColumn(internalRefColumn)\
                                            == metlinMatch.m_z)
        result.dropColumns(internalRefColumn)
        result.dropColumns("m_z__0")
    finally:
        if table.hasColumn(internalRefColumn):
            table.dropColumns(internalRefColumn)
    return result


