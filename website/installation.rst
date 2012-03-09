.. _installation:

Installation
============


.. _before_you_start:

Before you start
~~~~~~~~~~~~~~~~

If you plan to use *eMZed* for more than one user we recommend to provide a
shared folder, which can be accessed by all targetted users. We call this the
*global exchange folder*.  *eMZed* will store databases, *XCMS* [xcms]_ related code there.
Further you can use this folder to exchange scripts and configuration settings.

You can use *eMZed* without such a folder. Then data is stored per user and
sharing of scripts will not work.

If you decide to make use of the global exchange folder,
**at least one of the users needs write access to this folder and should be the
first user who starts eMZed. Else eMZed will not be able to work correctly.**



Instructions
~~~~~~~~~~~~

For installing *eMZed* on Windows please follow **carefully** the stepwise instructions:

1. Install *Python XY* from http://www.pythonxy.com. 
    
    This is a Python
    distribution targetting scientific computing with Python. It contains the
    right versions of Python and the used libraries.

2. Install *R* from http://www.r-project.org. 

3. Download and install the current Versions of *pyOpenMS* and *eMZed* from http://emzed.ethz.ch/downloads.

   Now you should have a start icon on your Desktop.

4. Start *eMZed*.

5. At the first start you are asked for the *global exchange folder*. 
   See :ref:`before_you_start`.

   **If you do not want to use an global exchange folder, you can leave the input field empty.**

6. *eMZed* will now retrieve or update a metabolomics related subset of the *PubChem* database 
   from the web.
   If you have a global exchange folder the full download will be stored there.
   Checking for update is done each time you start *eMZed*.

   **If you provided a global exchange folder and have no write permissions to it, this step wil be skipped**.


7. *eMZed* will install or update the *XMCS*-code if needed. If you have a global exchange folder
   an *XCMS* [xcms]_ related code will be stored there, so further starts of *eMZed*  by local users
   will be much faster.

   **If you provided a global exchange folder and have no write permissions to it, this step wil be skipped**.



You can clone a  current developer snaphsot of *eMZed* from http://github.com/uweschmitt/emzed.


In case of trouble, please use the *eMZed group* at http://groups.google.com/group/emzed-users.



  

 


