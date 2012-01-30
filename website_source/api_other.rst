API helper modules
==================

.. automodule:: elements

.. pycon::

   import elements
   print elements.C
   print elements.C["m0"]
   print elements.C12
   print elements.C12["abundance"]

.. automodule:: mass

.. pycon::
 
   import mass
   print mass.C13
   print mass.of("C4H8O2")
   print mass.of("C4H8O2", C=elements.C13)

.. automodule:: abundance

.. pycon::

   import abundance
   print abundance.C
   print abundance.C[12]
   print abundance.C12
