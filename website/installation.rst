.. _installation:

Installation
============


.. _before_you_start:

Before you start
~~~~~~~~~~~~~~~~

If you plan to use *eMZed* for more than one user we recommend to provide a
shared folder, which can be accessed by all targeted users. We call this the
*global exchange folder*.  *eMZed* will store databases, and *R* related code
there.  Further you can use this folder to exchange scripts and configuration
settings.

You can use *eMZed* without such a folder. Then data is stored per user and
sharing of scripts will not work.

If you decide to make use of the global exchange folder,
**at least one of the users needs write access to this folder and should be the
first user who starts eMZed. Else eMZed will not be able to work correctly.**

For support
~~~~~~~~~~~

If you have problems installing *eMZed*, please use the discussion group
at http://groups.google.com/group/emzed-users


Updating on Windows
~~~~~~~~~~~~~~~~~~~

If you update from an older *eMZed* version based on *PythonXY*, the
recommeded way is to uninstall *PythonXY* and *pyOpenMS* first and to
install from scratch as described below.

Installing on Windows
~~~~~~~~~~~~~~~~~~~~~

We changed the installing instructions for the 64 bit Windows version of 
*eMZed* and do not rely on *Python XY* any more.
Further we updated *eMZed* to the newest version of *pyopenms*.

For installing *eMZed* on Windows please follow **carefully** the stepwise
instructions. **version numbers and file names matter**.

1. Install 64 bit Python 2.7 for Windows from http://www.python.org/download/

2. Download and run *numpy-MKL-1.7.X.win-amd64-py2.7.exe* from
   http://www.lfd.uci.edu/~gohlke/pythonlibs#numpy 

3. If you do not have *R* installed on your system, download and run 
    http://cran.r-project.org/bin/windows/base/R-3.0.0-win.exe
   **Please install *R* with administration rights, else you might get problems
   using  *R* functionalities from *eMZed*.**

4. In order to install all other needed Python packages 
   download and unpack 
   http://emzed.ethz.ch/downloads/windows_contrib_downloader.zip. 

   This archive contains a *README* file, which you should read carefully !

5. Download and install the latest version of *eMZed* from 
   http://emzed.ethz.ch/downloads/emzed_1.3.0_for_windows.zip

   Now you should have a start icon on your Desktop.

6. Start *eMZed*.

7. At the first start you are asked for the *global exchange folder*. 
   See :ref:`before_you_start`.

   **If you do not want to use an global exchange folder, you can leave the input field empty.**

8. *eMZed* will now retrieve or update a metabolomics related subset of the *PubChem* database 
   from the web.
   If you have a global exchange folder the full download will be stored there.
   Checking for update is done each time you start *eMZed*.

   **If you provided a global exchange folder and have no write permissions to it, this step wil be skipped**.

   **eMZed might freeze for some minutes during download. This is a known problem
   which we will fix with the next version**


9. *eMZed* will install or update the *XMCS*-code if needed. If you have a global exchange folder
   an *XCMS* [xcms]_ related code will be stored there, so further starts of *eMZed*  by local users
   will be much faster.

   **If you provided a global exchange folder and have no write permissions to it, this step wil be skipped**.


Installing on Ubuntu 12.04
~~~~~~~~~~~~~~~~~~~~~~~~~~

An more comfortable installation package is work in progress. 

For the current version of *eMZed* you need run the following instructions with
``sudo`` or you have to login as an administrator:

* ``apt-get install python2.7``
* ``apt-get install python-numpy``
* ``apt-get install python-scipy``
* ``apt-get install python-matplotlib``
* ``apt-get install python-setuptools``
* ``apt-get install python-pip``
* ``apt-get install python-qt4``
* ``apt-get install python-qwt5-qt4``
* ``apt-get install r-base``
* ``apt-get install netcdf-bin``
* ``apt-get install libnetcdf-dev``
* ``apt-get install libqt4-core libqt4-gui``
* ``pip install guiqwt`` (tested with version 2.2.0)
* ``pip install guidata`` (tested with version 1.5.0)
* ``pip install guidata`` (tested with version 1.5.0)
* ``pip install spyder==2.1.13`` 
* ``pip install pyflakes``
* ``pip install ipython``

* Open-MS 1.9: Download 
   * http://downloads.sourceforge.net/project/open-ms/OpenMS/OpenMS-1.9/OpenMS-1.9.0-Linux_64bit.deb

  and run 
   * ``sudo dpkg --install OpenMS-1.9.0-Linux_64.deb`` from the directory containing this download.

* Download pyOpenMS (see http://emzed.ethz.ch/downloads), unzip it and 
   * run ``install.sh``, choose "global install to".

* Download latest *eMZed* (see http://emzed.ethz.ch/downloads/emzed_files_1.x.y.zip)
  and unzip it. Creates folder ``emzed/``

Start ``python emzed.pyw`` in the extracted folder and follow the windows instruction above, beginning at item no. 5.
  

 


