#encoding: latin-1


def formula(mf):
    """
    Creates formula object which allows addition and subtraction:

    .. pycon::

       import ms   !onlyoutput
       mf1 = ms.formula("H2O")
       mf2 = ms.formula("NaOH")
       print str(mf1 + mf2)
       print str(mf1 + mf2 - mf1)


    """
    import libms.Chemistry.MolecularFormula as MF
    return MF(mf)


# vim: ts=4 et sw=4 sts=4

