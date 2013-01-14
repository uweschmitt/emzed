#encoding: utf-8


def matchMetlin(table, massColumn, ppm):
    table.requireColumn(massColumn)
    table.requireColumn("polarity")
    from libms.WebserviceClients.Metlin import MetlinMatcher

    polarities = set(table.polarity.values)
    assert len(polarities) == 1, "multiple polarities in table"
    polarity = polarities.pop()

    masses = [ "%.6f" % m for m in table.getColumn(massColumn).values ]

    internalRefColumn = "__metlin_massmatch"
    if table.hasColumn(internalRefColumn):
        table.dropColumns(internalRefColumn)
    table.addColumn(internalRefColumn, masses)

    try:
        metlinMatch = MetlinMatcher.query(masses, ppm, polarity)
        if metlinMatch is None:
            table.addColumn("molid", None)
            table.dropColumns(internalRefColumn)
            return table

        result = table.leftJoin(metlinMatch, table.getColumn(internalRefColumn)\
                                            == metlinMatch.inputmass)
        result.dropColumns(internalRefColumn)
        result.set(result.colFormats, "dppm__0", "%3.1f")
        result.dropColumns("inputmass__0")
    finally:
        if table.hasColumn(internalRefColumn):
            table.dropColumns(internalRefColumn)
    return result


