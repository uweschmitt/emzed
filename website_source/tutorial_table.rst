===================
Working with Tables
===================

Tables are a central data structure in mzExplore. We give a short demonstration of its capabilities


.. pycon::
   :suppress_output:

   import ms
   import tab
   import mass


.. pycon::

    substances=ms.loadCSV("example.csv")
    substances.info()



That is the table has two columns named *name* and *mf* and both
contain data of type ``str``.

This is a small table which we print the table on the console




.. pycon::

    substances._print()



If the table is to complex or large for printing, we have a graphical interface for inspecting the table.


.. pycon::

    ms.inspect(substances)  !noexec



Adding a new, computed column is easy. Here we introduce a new column *m0* which contains the monoisotopic masses corresponding to the contents of the *mf* column




.. pycon::

    print mass.of("H2O") # calculates monoisotopic weights



.. pycon::

    substances.addColumn("m0", substances.mf.apply(mass.of))
    substances._print()



We load another table




.. pycon::

    info=ms.loadCSV("information.csv") 
    info._print()



And use an SQL-like *LEFTJOIN* to match rows with the same molecular formula




.. pycon::

    joined=substances.leftJoin(info, substances.mf==info.mf)
    joined._print()

We want to get rid of non terrestial substances by filtering the rows





.. pycon::

    common = joined.filter(joined.onEarth__0==1)
    common._print()



The ``tab`` module contains some databases, eg the substances from pubchem 
categorized as *metabolomic compounds*




.. pycon::

    import tab # some standard tables
    pc = tab.pc_full 
    ms.inspect(pc)  !noexec



Before matching our data against the large pubchem table, we build an index on tthis table in order to speed up the following ``leftJoin`` call. Building an index is done by sorting the corresponding column




.. pycon::

    pc.sortBy("m0")
    matched=joined.leftJoin(pc, (joined.onEarth__0==1) & joined.m0.approxEqual(pc.m0, 15*MMU))



.. pycon::

    matched.meta=dict()



.. pycon::

    print matched.numRows()



.. pycon::

    ms.inspect(matched)  !noexec


Another way to identify compounds is to use the Metlin webpage which provides a formular for running queries against the database. This access is automated




.. pycon::

    common.addColumn("polarity", "-") # metlin need this
    matched2=ms.matchMetlin(common, "m0", ppm=15)
    ms.inspect(matched2) !noexec



Modules providing chemical data
===============================

The ``mass`` module provides the masses of an electron, a
proton or a neutron and all all important elements




.. pycon::

    print mass.e # electron



.. pycon::

    print mass.C, mass.C12, mass.C13



Further it helps to calculate masses of molecules from their sum
formula




.. pycon::

    print mass.of("C6H2O6")



.. pycon::

    print mass.of("C6H2O6", C=elements.C13)



The ``elements`` module provides information
of important elements




.. pycon::

    print elements.C



.. pycon::

    print elements.C13


``abundance`` is a module which provides the natural abundances of
common elements




.. pycon::

    print abundance.C



Analysing isotope patterns
==========================

As the ``Table`` objects provide powerfull matchings, all we need to
analyse isotope patterns occuring in feature tables is a way to generate
tables containing theese data. ``ms.isotopeDistributionTable``
does this 




.. pycon::

    tab = ms.isotopeDistributionTable("C4S4", minp=0.01)
    tab._print()



Non natural distributions as in marker experiments can be
simmulated too




.. pycon::

    iso=ms.isotopeDistributionTable("C4S4", C=dict(C12=0.5, C13=0.5))
    iso.replaceColumn("abundance", iso.abundance / iso.abundance.sum() * 100.0)
    iso._print()



The method can simulate the resolution of the used mass analyzer




.. pycon::

    tab = ms.isotopeDistributionTable("C4S4", R=10000, minp=0.01)
    tab._print()



Matching isotope patterns now works like this




.. pycon::

    iso=ms.isotopeDistributionTable("H2O", minp=1e-3)
    iso.addEnumeration()
    iso._print()



.. pycon::

    common.dropColumns("mf__0", "onEarth__0")
    matched=iso.leftJoin(common, iso.mass.approxEqual(common.m0, 1*MMU))
    matched._print()

"

Statistical Analysis
====================

The framework provides two methods for comparing two datasets by analysis of variance: classical *one way ANOVA* and
non parametric *Kruskal Wallis* analysis.

These methods work on tables (is anybody surprised ?) like
this




.. pycon::

    group1 = [ 1.0, 0.9, 1.2, 1.4, 2.1]
    group2 = [ 1.0, 2.2, 2.3, 1.9, 2.8, 2.3]

    t = ms.toTable("measurement", group1 + group2)

    indices = [1]*len(group1) + [2] * len(group2)
    print indices

    t.addColumn("group", indices)
    t._print()



``ms.oneWayAnova`` returns the correspoding *F* and *p* value, ``ms.kruskalWallis`` the *H* and *p* value




.. pycon::

    F, p = ms.oneWayAnova(t.group, t.measurement)
    print p



.. pycon::

    H, p = ms.kruskalWallis(t.group, t.measurement)
    print p



Building graphical interfaces
=============================

Beyond the ``Table``-Explorer ``ms.inspect`` and the
Peakmap-Explorer ``ms.inspectPeakMap`` assisted workflows
request certain parameters and decisions at certain processing steps. To support this mzExplore has an builder for
graphical input forms




.. pycon::

    b=ms.DialogBuilder(title="Please provide data")
    b.addInstruction("For Algorithm A please provide")
    b.addInt("Level")
    b.addFloat("Threshold")
    b.addFileOpen("Input File")
    print b.show()                            !noexec


    print help(ms.DialogBuilder)
