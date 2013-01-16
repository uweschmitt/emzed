===============
Getting Started
===============


.. figure:: emzed_workbench_overview.png
   :scale: 75 %



How to change the working directory?
------------------------------------



Scripts and data of the working directory can be directly accessed and executed, respectively. 

.. figure:: emzed_working_dir.png
   :scale: 75 %

To change the working directory 

1. Press the "choose folder button" of eMZed taskbar (1.) and choose directory. 

2. Press "set button" (2.) to set the current working directory to the chosen one.

After pressing the "set button" the new working directory is diplayed in the IPython console.

.. figure:: emzed_working_dir_cwd.png
   :scale: 75%
  

You can verify the current working directory by typing ``pwd`` in the IPython console. Press ``Enter``, type ``pwd`` and press ``Enter`` again.

.. figure:: emzed_working_dir_pwd.png
   :scale: 75 %

You can display the content of the working directory with ``ls``.




How to to work with the IPython console?
----------------------------------------


To get online help on IPython console type ``help()``.
IPython console allows you to run scripts or execute commands.
Here is a very simple example how to use the console:

.. figure:: ipython_code.png
   :scale: 75 %

The command creates a string object called``welcome``. With the print command the content of ``welcome`` is diplayed in the console. The console provides command completion and automatic dialog boxes showing a list of possible methods which can be applied to the object ``welcome``. In the same way, available methods on any type of object are shown automaticaly. You can activate command completion after any character by pressing the ``Tab`` button. All methods which can be applied to the object are displayed in the console by typing the name of the object + ".". For given example:

.. figure:: ipython_object_operations.png
   :scale: 75 %

We will now apply the function ``capitalize()`` to the string ``welcome``. You get the documentation of ``capitalize()`` by typing:

.. figure:: ipython_object_function_documentation.png
   :scale: 75 %

We can now to apply the function ``capitalize()`` to the object ``welcome``:

.. figure:: ipython_apply_function.png
   :scale: 75 %


The result of the last commamnd executed in the IPython console is always accessible via underscore ``"_"``. 
In case you forgot to assign a variable name to a result you can do that afterwards by using the underscore ``"_"``.

.. figure:: ipython_working_with__.png 
   :scale: 75 %


You can find a more detailed IPython tutorial here_.
 
.. _here: http://ipython.org/ipython-doc/stable/interactive/tutorial.html




How to run scripts / workflows?
-------------------------------



You can use the **Editor** to write scripts and functions which can be executed in the IPython console. Here is a very simple example.
We will create a function that calculates the mass of H2O:

.. figure:: using_editor_code.png
   :scale: 75 %

Type the code into the editor and save it into your working directory. 

There are two possibilities to run scripts in eMZed. 

(1) You can execute the script currently displayed in the Editor  by simply pressing the **``F5``** button. When the script is executed the first time a dialog box will open. Choose the first option "Execute in current IPython or Python interpreter". 

.. figure:: run_script.png
   :scale: 75 %


After executing the script all functions of the script are now available in the IPython console. Type the name of the function and press ``Enter`` to execute it.

.. figure:: run_script_executing.png
   :scale: 75 % 


(2) You can also use the command **``runfile``**. If the file is saved in the working directory you simply type ``runfile("filename.py")`` in the IPython console. For given example: 

.. figure:: run_script_alternative.png
   :scale: 75 %

If the script is not located in the working directory you have to add the path of the script to its name: ``runfile(".../folder/filename.py")``. 





How to use eMZed modules?
-------------------------


As an *Example* we determine the isotope distribution of molecular formula *C6H13O9P*. It can be calculated using the method *isotopeDistributionTable* of the main eMZed module **ms**. After typing ``ms.`` the autocompletion shows all methods of the module ms. 

.. figure:: ipython_autocompletion.png
   :scale: 75 %

You can reduce the number of methods by typing ms.i and pressing the ``Tab`` button. 

.. figure:: ipython_tab_button.png
   :scale: 75 %


- To get help on the function type ``ms.isotopeDistributionTable?`` or ``help(ms.isotopeDistributionTable)`` and press ``Enter``.

.. figure:: emzed_modules_help.png
   :scale: 75 %


- To execute the function type with default parameter settings type  ``isotopes=ms.isotopeDistributionTable("C6H13O9P")`` and press ``Enter``. 

.. figure:: ipython_execute_function.png
   :scale: 75 %

To inspect the table object see below_.


How to inspect objects?
-----------------------

.. _below:

The variable explorer provides an easy way to inspect objects. All object names and their properties are listed in the variable explorer.  Here an example:

.. figure:: variable_explorer.png
   :scale: 75 %

To visualize the content of the variable ``isotopes`` double click the row and a new window with the table explorer opens:

.. figure:: table_explorer.png
   :scale: 75 %

Some objects like e.g. tables have a print method. type ``table_name.print_()`` and you can directly print the result in the console.

.. figure:: table_print().png
   :scale: 75 %



More about Python
-----------------

To write your own skripts basic knowledge in Python is mandatory. However, Python is easy to learn.

**To get an introduction into Python language** try this one_.

.. _one: https://developers.google.com/edu/python/ 









