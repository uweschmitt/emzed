=============
A Guided Tour
=============

.. image:: eMZed.png
   :scale: 50 %

.. _ipython_example:

Working with iPython command line
---------------------------------

eMZed is based on open source python language. You can directly execute commands in the console and examples below can be directly executed in the command line. 
Most functions and operation are found in the module ms. The console provides command completion and automatic dialog boxes showing a list of possible commands. 
In the same way, possible operations on any type of object (variable type) are indicated automaticaly.

.. image:: console_code_completion.png
   :scale: 60 %  



.. _peakmaps_example:

Working with PeakMaps
---------------------
eMZed allows loading, inspecting and basic filtering of LC-MS(/MS) data files. To load your single data files to the workspace use the command:

.. pycon::
   :invisible:
 
   import ms
   ds=ms.loadPeakMap() 

.. pycon::

   
   ds = ms.loadPeakMap() !noexec
   help(ms.loadPeakMap)  


The peakmap 'ds' will appear in the variable explorer window and you can open the peakmap by simply double clicking the variable ds.

.. image:: peakmap_variable_explorer.png
   :scale: 60 %
   
Alternatively use the command

.. pycon::
   ms.inspectPeakMap(ds) !noexec

.. image:: inspect_peakmap1.png
   :scale: 50 %
   

The upper plot shows the TIC and the lower plot the ms spectrum indicated by the bar with the center dot. 

.. image:: inspect_peakmap2.png
   :scale: 50 %

A.You can move the bar with the mouse when you click on the bar with the left 
mouse button keeping the button pressed. B. m/z values of mass peaks in spectrum are depicted. In addition you can measure distance and relative intensity of a mass peak relative to
a selected one. It is also possible to select mass peaks of a spectrum and extract corresponding ion chromatograms. 

extracting mz traces

.. _centwave_example:

Exctracting chromatographic peaks
---------------------------------

Actually, eMZed includes two peak detection algorithm of the XCMS package: centwave and matched filter. Excepted input file formats are mxML, mzXML, and mzData.
The output file format is .table. In addition .csv files are saved.

We continue with an example of centwave algorithm for high resolution LC-MS data. 

.. pycon::
   import batches
   tables=batches.runCentwave("V:/pkiefer/eMZed/MZXML/*.mzXML", ppm=10, peakwidth=(15,60), prefilter=(5,10000),snthresh=0.1,mzdiff=0.001) !noexec

Various parameters can be adapted.For details type

.. pycon::
   help(batches.centwave) !noexec


.. image:: tableListVarBrowser.png
   :scale: 50 %
 
The resulting output file is a list containing 3 table objects (see working with tables). You can open the table list by double clicking the variable tab in the variable explorer. 
Click on choose to switch between different tables. In each table parameters of detected peaks are depicted row wise. You can visualize corresponding Extracted Ion Chromatograms 
**(EIC)** and mass spectra by clicking the left line button. Tables are editable and all modifications are in place. 
Notice that the original peakmap is linked to table and raw data are accessible.



.. image:: table_explorer.png
   :scale: 60 %


.. _integration_example:

Integrating Features
--------------------

Detected Peaks can be integrated. To perform peak integration columns rtmin, rtmax, mzmin, and mzmax are mandatory.  To reduce the runtime we will choose 1 table out of the list
and we will only integrate those peaks with a signal to noise >5e4.

.. pycon::
   tab=tables[0] !noexec
   tabFilt=tab.filter(tab.sn>5e4) !noexec
   tabInt=ms.integrate(tabFilt, 'emg_exact') !noexec


.. image:: table_integrate.png
   :scale: 60 %

For all peaks integrated peaks area and rmse values are automatically added to the table (A). You can manualy reintegrate individual EIC peaks applying one aout of 6 different integration methods thereby adapting the window width for peak integration changing any other 
entry (B). For more details see **LINK**


.. _rtalign_example:

Aligning Features
-----------------
The retention time alignment is performed with the  `OpenMS <http://open-ms.sourceforge.net/openms/>`_ 
map alignment algorithm and aligns a list of  tables to a reference table.

.. pycon::
   tablesAligned=ms.rtAlign(tables) !noexec

To visualize the rt shift on tables we will now overlay two tables before and after rt alignment. We are reducing again the
number of peaks in the table by filtering for a minimum SN level. To get the overlay before the rt alignemnt

.. pycon::
   tab1=tables[0] !noexec
   tab1=tab1.filter(tab1.sn>5e4) !noexec
   tab2=tables[2] !noexec
   tab2=tab2.filter(tab2.sn>5e4) !noexec
   before=tab1.join(tab2, tab1.mz.approxEqual(tab2.mz, 3*MMU) &tab1.rt.approxEqual(tab2.rt,30))   !noexec   

Open the table 'before' and sort the peak in ascending order with column 'sn' and click on column with id=191.
And now repeat the same procedure for the same tables after rt alignemnt:

.. pycon::
   tabA1=tablesAligned[0] !noexec
   tabA1=tabA1.filter(tabA1.sn>5e4) !noexec
   tabA2=tablesAligned[2] !noexec
   tabA2=tabA2.filter(tabA2.sn>5e4) !noexec
   after=tabA1.join(tabA2, tabA1.mz.approxEqual(tabA2.mz, 3*MMU) &tabA1.rt.approxEqual(tabA2.rt,30)) !noexec

Open now the table 'after' and sort the peak in ascending order with column 'sn' and click again on column with id=191.

.. image:: rtalignment.png
   :scale: 60 %

The plot shows the overlay of two EIC peaks of the same compound in two different samples before (A) and after (B) retention time alignment.


.. _table_example:

Working with Tables
-------------------



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

    substances.print_()



If the table is to complex or large for printing, we have a graphical interface for inspecting the table.


.. pycon::

    ms.inspect(substances)  !noexec



Adding a new, computed column is easy. Here we introduce a new column *m0* which contains the monoisotopic masses corresponding to the contents of the *mf* column




.. pycon::

    print mass.of("H2O") # calculates monoisotopic weights



.. pycon::

    substances.addColumn("m0", substances.mf.apply(mass.of))
    substances.print_()



We load another table




.. pycon::

    info=ms.loadCSV("information.csv") 
    info.print_()



And use an SQL-like *LEFTJOIN* to match rows with the same molecular formula




.. pycon::

    joined=substances.leftJoin(info, substances.mf==info.mf)
    joined.print_()

We want to get rid of non terrestial substances by filtering the rows





.. pycon::

    common = joined.filter(joined.onEarth__0==1)
    common.print_()



The ``tab`` module contains some databases, eg the substances from pubchem 
categorized as *metabolomic compounds*




.. pycon::

    import tab # some standard tables
    pc = tab.pc_full 
    ms.inspect(pc)  !noexec



Before matching our data against the large pubchem table, we build an index on tthis table in order to speed up the following ``leftJoin`` call.
Building an index is done by sorting the corresponding column




.. pycon::

    pc.sortBy("m0")
    matched=joined.leftJoin(pc, (joined.onEarth__0==1) & joined.m0.approxEqual(pc.m0, 15*MMU))
    print matched.numRows()
    ms.inspect(matched)  !noexec


Another way to identify compounds is to use the Metlin webpage which provides a formular for running queries against the database. This access is automated




.. pycon::

    common.addColumn("polarity", "-") # metlin need this
    matched2=ms.matchMetlin(common, "m0", ppm=15)
    ms.inspect(matched2) !noexec


.. _chemistry_example:

Accessing Chemical Data
-----------------------


The ``mass`` module provides the masses of an electron, a
proton or a neutron and all all important elements




.. pycon::

    print mass.e # electron
    print mass.C, mass.C12, mass.C13



Further it helps to calculate masses of molecules from their sum
formula




.. pycon::

    print mass.of("C6H2O6")



.. pycon::

    import elements
    print mass.of("C6H2O6", C=elements.C13)



The ``elements`` module provides information
of important elements




.. pycon::

    print elements.C
    print elements.C13


``abundance`` is a module which provides the natural abundances of
common elements


.. pycon::

    import abundance     !nooutput
    print abundance.C


.. _isotope_example:

Analysing isotope patterns
--------------------------

As the ``Table`` objects provide powerfull matchings, all we need to
analyse isotope patterns occuring in feature tables is a way to generate
tables containing theese data. ``ms.isotopeDistributionTable``
does this 




.. pycon::

    tab = ms.isotopeDistributionTable("C4S4", minp=0.01)
    tab.print_()



Non natural distributions as in marker experiments can be
simmulated too




.. pycon::

    iso=ms.isotopeDistributionTable("C4S4", C=dict(C12=0.5, C13=0.5))
    iso.replaceColumn("abundance", iso.abundance / iso.abundance.sum() * 100.0)
    iso.print_()



The method can simulate the resolution of the used mass analyzer




.. pycon::

    tab = ms.isotopeDistributionTable("C4S4", R=10000, minp=0.01)
    tab.print_()



Matching isotope patterns now works like this




.. pycon::

    iso=ms.isotopeDistributionTable("H2O", minp=1e-3)
    iso.addEnumeration()
    iso.print_()



.. pycon::

    common.dropColumns("mf__0", "onEarth__0")
    matched=iso.leftJoin(common, iso.mass.approxEqual(common.m0, 1*MMU))
    matched.print_()



.. _statistics_example:

Statistical Analysis
--------------------


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
    t.print_()



``ms.oneWayAnova`` returns the correspoding *F* and *p* value, ``ms.kruskalWallis`` the *H* and *p* value




.. pycon::

    F, p = ms.oneWayAnova(t.group, t.measurement)
    print p



.. pycon::

    H, p = ms.kruskalWallis(t.group, t.measurement)
    print p



.. _dialogbuilder_example:

Building graphical interfaces
-----------------------------

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
