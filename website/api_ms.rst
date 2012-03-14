API ms Module
=============

.. automodule:: ms

MZ Alignment
~~~~~~~~~~~~

.. autofunction:: ms.mzAlign


RT Alignment
~~~~~~~~~~~~

For an example see :ref:`rtalign_example`

.. autofunction:: ms.rtAlign
   


Inspecting Tables and Peakmaps
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


.. autofunction:: ms.inspectPeakMap
.. autofunction:: ms.inspect

For more information about using these Explorers see :ref:`explorers`. 


Integrating Peaks
~~~~~~~~~~~~~~~~~

.. autofunction:: ms.integrate


Simulating Isotope Distributions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autofunction:: ms.isotopeDistributionTable

    Examples:

    .. pycon::

       import ms !nooutput
       # natural abundances:
       tab = ms.isotopeDistributionTable("C3H7NO2")
       tab.abundance /= tab.abundance.sum()
       tab.print_()

       # artifical abundances:
       tab = ms.isotopeDistributionTable("C3H7NO2", C=dict(C13=0.5, C12=0.5))
       tab.abundance /= tab.abundance.sum()
       tab.print_()

.. autofunction:: ms.plotIsotopeDistribution


    .. pycon::
    
       ms.plotIsotopeDistribution("C3H7NO2", C=dict(C13=0.5, C12=0.5), R=5000) !noexec

    .. image:: isopattern_alanin.png 


Statistics
~~~~~~~~~~

.. autofunction:: ms.oneWayAnova
.. autofunction:: ms.kruskalWallis

see :ref:`statistics_example` for example usage

.. autofunction:: ms.oneWayAnovaOnTables

   Compares two sets of tables. Eg.:

.. pycon::
   :invisible:

   t = ms.toTable("id", ["ATP", "ADP"])
   t.addColumn("n1", [4,5])
   t.addColumn("n2", [6,6])
   t.addColumn("avg1_foldChange", [1.4, 1.6])
   t.addColumn("std1_foldChange", [0.4, 0.13])
   t.addColumn("avg2_foldChange", [0.4, 1.5])
   t.addColumn("std2_foldChange", [0.3, 0.08])
   t.addColumn("p_value", [0.9, 0.23])
   tresult=t


.. pycon::
   tresult = ms.oneWayAnovaOnTables(tables1, tables2, idColumn="compound", valueColumn="foldChange") !noexec
   tresult.print_()

.. autofunction:: ms.kruskalWallisOnTables

   Same as :py:meth:`~ms.oneWayAnovaOnTables` above.

Online Feature Matching
~~~~~~~~~~~~~~~~~~~~~~~

.. autofunction:: ms.matchMetlin

   *table* needs ``polarity`` column. Example:

.. pycon::
   t = ms.toTable("mz", [291.1064, 583.22282])
   t.addColumn("polarity", "-")
   matched = ms.matchMetlin(t, "mz", 30)
   matched.print_()


Helpers
~~~~~~~

.. autofunction:: ms.mergeTables
.. autofunction:: ms.toTable
.. autofunction:: ms.openInBrowser

Simple Dialogs
~~~~~~~~~~~~~~

.. autofunction:: ms.askForDirectory
.. autofunction:: ms.askForSave
.. autofunction:: ms.askForSingleFile
.. autofunction:: ms.askForMultipleFiles
.. autofunction:: ms.showWarning
.. autofunction:: ms.showInformation


DialogBuilder
~~~~~~~~~~~~~

For an example see  :ref:`dialogbuilder_example`

.. autoclass:: ms.DialogBuilder

I/O
~~~

.. autofunction:: ms.storePeakMap
.. autofunction:: ms.storeCSV
.. autofunction:: ms.storeTable


