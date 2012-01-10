
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
        table.dropColumn(internalRefColumn)
    table.addColumn(internalRefColumn, masses)

    try:
        metlinMatch = MetlinMatcher.query(masses, ppm, polarity)
        if metlinMatch is None:
            table.addColumn("molid", None)
            table.dropColumn(internalRefColumn)
            return table

        result = table.leftJoin(metlinMatch, table.getColumn(internalRefColumn)\
                                            == metlinMatch.inputmass)
        result.dropColumn(internalRefColumn)
    finally:
        if table.hasColumn(internalRefColumn):
            table.dropColumn(internalRefColumn)
    return result


