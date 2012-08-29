#encoding: latin-1


def formula(mf):
    """
    Creates formula object which allows addition and subtraction:

    .. pycon::

       import ms   !onlyoutput
       mf1 = ms.formula("H2O")
       mf2 = ms.formula("NaOH")
       mf3 = mf1 + mf2
       print str(mf3)
       print str(mf3 - mf1)

    Mass calculation is supported too:

    .. pycon::

       print mf1.mass()

    If you need some internal representation, you can get a dictionary.
    Keys are pairs of *(symbol, massnumber)*, where *massnumber = None*
    refers to the lowest massnumber. Values of the dictionary are counts:

    .. pycon::

       print mf1.asDict()
       mixed = ms.formula("[13]C2[14]C3")
       print mixed.asDict()


    """
    import libms.Chemistry.MolecularFormula as MF
    return MF(mf)


# vim: ts=4 et sw=4 sts=4

