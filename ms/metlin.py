import pdb

def matchMetlin(table, massColumn, ppm):
    table.requireColumn(massColumn)
    table.requireColumn("polarity")
    from libms.WebserviceClients.Metlin import MetlinMatcher

    polarities = set(table.polarity.values)
    assert len(polarities) == 1, "multiple polarities in table"
    polarity = polarities.pop()

    masses = [ "%.6f" % m for m in table.getColumn(massColumn).values ]
    table.addColumn("__massmatch", masses)

    metlinMatch = MetlinMatcher.query(masses, ppm, polarity)
    if metlinMatch is None:
        table.addColumn("molid", None)
        table.dropColumn("__masmatch")
        return table

    result = table.leftJoin(metlinMatch, table.__massmatch == metlinMatch.inputmass)
    result.dropColumn("__massmatch")
    return result


