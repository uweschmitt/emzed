Cookbook -- Solutions for common problems
=========================================

How do I get all files in a given directory with given file extension ?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. pycon::
   import glob
   print glob.glob("examples\\*.mzXML") !noexec
   print ["examples/data1.mzXML", "examples/data2.mzXML"] !onlyoutput
   


How do I drop columns based on some criterion ?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The following code gives does not work correctly:

.. pycon::
   for name in t.colNames:  !noexec
       if name.endswith("__0"):  !noexec
            t.dropColumns(name)  !noexec


This code will in most cases not delete all columns with a name ending
with "__0" as the columnames we iterate over change during iteration.

With the little modification in the *for* statment the code
works, we iterate over **a copy** of the list containing the column
names:

.. pycon::
   for name in t.colNames[:]:  !noexec
       if name.endswith("__0"):  !noexec
            t.dropColumns(name)  !noexec

