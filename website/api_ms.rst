API ms Module
=============

.. automodule:: ms

MZ Alignment
~~~~~~~~~~~~

.. autofunction:: ms.mzalign


RT Alignment
~~~~~~~~~~~~

For an example see :ref:`rtalign_example`

.. autofunction:: ms.rtalign
   


Inspecting Tables and Peakmaps
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For example usage see...

.. autofunction:: ms.inspectPeakMap
.. autofunction:: ms.inspect


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

.. autofunction:: ms.oneWayAnovaOnTables
.. autofunction:: ms.kruskalWallisOnTables

Online Feature Matching
~~~~~~~~~~~~~~~~~~~~~~~

.. autofunction:: ms.matchMetlin

Helpers
~~~~~~~

.. autofunction:: ms.mergeTables
.. autofunction:: ms.toTable
.. autofunction:: ms.openInBrowser
.. autofunction:: ms.unpack

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

.. autofunction:: ms.storeCSV
.. autofunction:: ms.storeTable


