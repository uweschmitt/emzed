Working with tables
===================


.. autoclass:: libms.DataStructures.Table
   :members:


The class *Table* fullfills the iterator proctocol. So the following
snippet prints all values of the column *mz*::

     for row in table:
         print table.get(row, "mz")


