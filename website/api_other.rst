API helper modules
==================

.. automodule:: elements

.. pycon::
   :invisible:

   import elements
   import mass
   import abundance

Data of chemical elemets are available from the *elements* module, e.g:

.. pycon::

   print elements.C
   print elements.C["m0"]
   print elements.C12
   print elements.C12["abundance"]

.. automodule:: mass


Masses can be quried like this:

.. pycon::
 
   print mass.C13
   print mass.of("C4H8O2")

Nested formulas are supported:

.. pycon::

   print mass.of("C(CH2)4COOH")

And isotopes can be specified in brackets:

.. pycon::

   print mass.of("[13]C4H8O2")
   print mass.of("[13]CC2H8O2")

.. automodule:: abundance

.. pycon::

   print abundance.C
   print abundance.C[12]
   print abundance.C12
