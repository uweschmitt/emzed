API helper modules
==================

.. automodule:: elements

.. pycon::
   :invisible:

   import elements
   import mass
   import abundance

.. pycon::

   print elements.C
   print elements.C["m0"]
   print elements.C12
   print elements.C12["abundance"]

.. automodule:: mass

.. pycon::
 
   print mass.C13
   print mass.of("C4H8O2")
   print mass.of("C4H8O2", C=elements.C13)

.. automodule:: abundance

.. pycon::

   print abundance.C
   print abundance.C[12]
   print abundance.C12
