========
Tutorial
========


Working with Tables
===================

Tables are a central data structure in mzExplore. We give a short demonstration of its capabilities::


    >>> substances=ms.loadCSV("example.csv")
    >>> substances.info()
    
    table info:   title= example.csv
    
       meta={'loaded_from': 'D:\\msWorkbench\\example.csv'}
       len= 4
    
       #0  [4 diff vals, 0 Nones]    name='name'   <type 'str'>    fmt='%s'
       #1  [4 diff vals, 0 Nones]    name='mf'     <type 'str'>    fmt='%s'
    
    


That is the table has two columns named *name* and *mf* and both
contain data of type ``str``.

This is a small table which we print the table on the console::


    >>> substances._print()
    name         mf          
    str          str         
    ------       ------      
    water        H2O         
    sodium       NaCl        
    fullerene    C18         
    cryptonite   Kr          
    


If the table is to complex or large for printing, we have a graphical interface for inspecting the table:


    >>> ms.inspect(substances)
    


Adding a new, computed column is easy. Here we introduce a new column *m0* which contains the monoisotopic masses corresponding to the contents of the *mf* column::


    >>> print mass.of("H2O") # calculates monoisotopic weights
    18.0105650638
    
    >>> substances.addColumn("m0", substances.mf.apply(mass.of))
    >>> substances._print()
    name         mf           m0          
    str          str          float       
    ------       ------       ------      
    water        H2O          18.01057    
    sodium       NaCl         57.95862    
    fullerene    C18          216.00000   
    cryptonite   Kr           -           
    


We load another table::


    >>> info=ms.loadCSV("information.csv") # without path -> opens dialog
    >>> info._print()
    mf           onEarth     
    str          int         
    ------       ------      
    H2O          1           
    NaCl         1           
    HCl          1           
    Kr           0           
    


And use an SQL-like *LEFTJOIN* to match rows with the same molecular formula::


    >>> joined=substances.leftJoin(info, substances.mf==info.mf)
    >>> joined._print()
    name         mf           m0           mf_1         onEarth_1   
    str          str          float        str          int         
    ------       ------       ------       ------       ------      
    water        H2O          18.01057     H2O          1           
    sodium       NaCl         57.95862     NaCl         1           
    fullerene    C18          216.00000    -            -           
    cryptonite   Kr           -            Kr           0           
    
We want to get rid of non terrestial substances by filtering the rows
::


    >>> common = joined.filter(joined.onEarth_1==1)
    >>> common._print()
    name         mf           m0           mf_1         onEarth_1   
    str          str          float        str          int         
    ------       ------       ------       ------       ------      
    water        H2O          18.01057     H2O          1           
    sodium       NaCl         57.95862     NaCl         1           
    


The ``tab`` module contains some databases, eg the substances from pubchem 
categorized as *metabolomic compounds*::


    >>> import tab # some standard tables
    >>> pc = tab.pc_full
    >>> ms.inspect(pc)


Before matching our data against the large pubchem table, we build an index on tthis table in order to speed up the following ``leftJoin`` call. Building an index is done by sorting the corresponding column::


    >>> pc.sortBy("m0")
    >>> matched=joined.leftJoin(pc, (joined.onEarth_1==1) 
    >>>                            & joined.m0.approxEqual(pc.m0, 15*MMU))
    >>> ms.inspect(matched)
    

Another way to identify compounds is to use the Metlin webpage which provides a formular for running queries against the database. This access is automated::


    >>> common.addColumn("polarity", "-") # metlin need this
    >>> matched2=ms.matchMetlin(common, "m0", ppm=15)
    >>> ms.inspect(matched2)
    


Modules providing chemical data
===============================

The ``mass`` module provides the masses of an electron, a
proton or a neutron and all all important elements::


    >>> print mass.e # electron
    0.00054857990946
    
    >>> print mass.C, mass.C12, mass.C13
    12.0 12.0 13.003355
    


Further it helps to calculate masses of molecules from their sum
formula::


    >>> print mass.of("C6H2O6")
    169.985140064
    
    >>> print mass.of("C6H2O6", C=elements.C13)
    176.005270064
    


The ``elements`` module provides information
of important elements::


    >>> print elements.C
    {'massnumber': 12, 'm0': 12.0, 'number': 6, 'name': 'Carbon'}
    
    >>> print elements.C13
    {'abundance': 0.010700000000000001, 'name': 'Carbon', 'number': 6, 'mass': 13.003355}
    

``abundance`` is a module which provides the natural abundances of
common elements::


    >>> print abundance.C
    {12: 0.9893000000000001, 13: 0.010700000000000001}
    


Analysing isotope patterns
==========================

As the ``Table`` objects provide powerfull matchings, all we need to
analyse isotope patterns occuring in feature tables is a way to generate
tables containing theese data. ``ms.isotopeDistributionTable``
does this:: 


    >>> tab = ms.isotopeDistributionTable("C4S4", minp=0.01)
    >>> tab._print()
    mf           mass         abundance   
    str          float        float       
    ------       ------       ------      
    C4S4         175.888283   1.000       
    C4S4         176.887670   0.032       
    C4S4         176.891638   0.043       
    C4S4         177.884079   0.181       
    


Non natural distributions as in marker experiments can be
simmulated too::


    >>> iso=ms.isotopeDistributionTable("C4S4", C=dict(C12=0.5, C13=0.5))
    >>> iso.replaceColumn("abundance", iso.abundance / iso.abundance.sum() * 100.0)
    >>> iso._print()
    mf           mass         abundance   
    str          float        float       
    ------       ------       ------      
    C4S4         175.888283   5.40        
    C4S4         176.891638   21.59       
    C4S4         177.894993   32.38       
    C4S4         178.887434   3.90        
    C4S4         178.898348   21.59       
    C4S4         179.890789   5.85        
    C4S4         179.901703   5.40        
    C4S4         180.894144   3.90        
    


The method can simulate the resolution of the used mass analyzer::


    >>> tab = ms.isotopeDistributionTable("C4S4", R=10000, minp=0.01)
    >>> tab._print()
    mf           mass         abundance   
    str          float        float       
    ------       ------       ------      
    C4S4         175.888283   1.000       
    C4S4         176.889972   0.073       
    C4S4         177.884079   0.181       
    


Matching isotope patterns now works like this::


    >>> iso=ms.isotopeDistributionTable("H2O", minp=1e-3)
    >>> iso.addEnumeration()
    >>> iso._print()
    id           mf           mass         abundance   
    int          str          float        float       
    ------       ------       ------       ------      
    0            H2O          18.010565    1.000       
    1            H2O          20.014819    0.002       
    
    >>> common.dropColumns("mf_1", "onEarth_1")
    >>> matched=iso.leftJoin(common, iso.mass.approxEqual(common.m0, 1*MMU))
    >>> matched._print()
    id           mf           mass         abundance    name_1       mf_1         m0_1         polarity_1  
    int          str          float        float        str          str          float        str         
    ------       ------       ------       ------       ------       ------       ------       ------      
    0            H2O          18.010565    1.000        water        H2O          18.01057     -           
    1            H2O          20.014819    0.002        -            -            -            -           
    
"

Statistical Analysis
====================

The framework provides two methods for comparing two datasets by analysis of variance: classical *one way ANOVA* and
non parametric *Kruskal Wallis* analysis.

These methods work on tables (is anybody surprised ?) like
this::


    >>> t._print()
    group        measurement 
    int          float       
    ------       ------      
    1            0.90000     
    1            1.00000     
    2            1.00000     
    1            1.20000     
    1            1.40000     
    2            1.90000     
    1            2.10000     
    2            2.20000     
    2            2.30000     
    2            2.30000     
    2            2.80000     
    


``ms.oneWayAnova`` returns the correspoding *F* and *p* value, ``ms.kruskalWallis`` the *H* and *p* value::


    >>> F, p = ms.oneWayAnova(t.group, t.measurement)
    >>> print p
    0.0480721067923
    
    >>> H, p = ms.kruskalWallis(t.group, t.measurement)
    >>> print p
    0.0541290285797
    


Building graphical interfaces
=============================

Beyond the ``Table``-Explorer ``ms.inspect`` and the
Peakmap-Explorer ``ms.inspectPeakMap`` assisted workflows
request certain parameters and decisions at certain processing steps. To support this mzExplore has an builder for
graphical input forms::


    >>> b=ms.DialogBuilder(title="Please provide data")
    >>> b.addInstruction("For Algorithm A please provide")
    >>> b.addInt("Level")
    >>> b.addFloat("Threshold")
    >>> b.addFileOpen("Input File")
    >>> print b.show()
    (1, 0.007, u'D:/msWorkbench/data.mzML')
    
