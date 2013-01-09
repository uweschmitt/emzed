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

In Case of trouble
~~~~~~~~~~~~~~~~~~

If you have problems installing *eMZed*, please use the discussion group
at http://groups.google.com/group/emzed-users



Installing on Windows
~~~~~~~~~~~~~~~~~~~~~

For installing *eMZed* on Windows please follow **carefully** the stepwise instructions:

1. Install *Python XY* (http://www.pythonxy.com). 

   *Python XY* is a Python distribution targeting scientific computing with
   Python. It contains the right versions of Python and the some needed
   libraries.  If you use other distributions as *Enthought Python* the
   following instructions are not complete anymore.

   *eMZed* requires the latest  *2.7.2.x* version.

   Finding distinct versions at the *Python XY* website is difficult and
   downloads may be **mistaken** with the *Python XY* **update intstallers**,
   which do not provide the full Python distribution.

   You can find full installers of recent *Python XY* versions at:

    * http://ftp.ntua.gr/pub/devel/pythonxy/
    * http://pythonxy.connectmv.com/
    * http://www.mirrorservice.org/sites/pythonxy.com


   

2. Install *R* from http://www.r-project.org. 

   Please install *R* with administration rights, else you might get problems
   using  *R* functionalities from *eMZed*.

3. Download and install the latest version of *pyOpenMS* and *eMZed* from http://emzed.ethz.ch/downloads.

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


Installing on Ubuntu 12.04
~~~~~~~~~~~~~~~~~~~~~~~~~~

An more comfortable installation package is work in progress. 

For the current version of *eMZed* you need run the following instructions with
``sudo`` or you have to login as an adminstrator:

* ``apt-get install python2.7``
* ``apt-get install python-numpy``
* ``apt-get install python-scipy``
* ``apt-get install python-matplotlib``
* ``apt-get install python-pip``
* ``apt-get install python-qt4``
* ``apt-get install python-qwt5-qt4``
* ``apt-get install r-base``
* ``apt-get install netcdf-bin``
* ``apt-get install libnetcdf-dev``
* ``apt-get install libqt4-core libqt4-gui``

* ``sudo pip install guiqwt`` (tested with version 2.2.0)
* ``sudo pip install guidata`` (tested with version 1.5.0)

Then install

* IPython 0.10. 
   * Download archive http://archive.ipython.org/release/0.10.2/ipython-0.10.2.tar.gz 
  unpack it and run
   * ``python setup.py install``

* Open-MS 1.8: Download 
   * http://downloads.sourceforge.net/project/open-ms/OpenMS/OpenMS-1.9/OpenMS-1.9.0-Linux_64bit.deb

  and run 
   * ``sudo dpkg --install OpenMS-1.9.0-Linux_64.deb`` from the directory containing this download.

* Download pyOpenMS (see http://emzed.ethz.ch/downloads), unzip it and 
   * run ``install.sh``, choose "global install to".

* Dowload latest *eMZed* (see http://emzed.ethz.ch/downloads/emzed_files_1.x.y.zip)
  and unzip it. Creates folder ``emzed/``

Start ``python emzed.pyw`` in the extracted folder and follow the windows instruction above, beginning at item no. 5.



Help
~~~~

In case of any trouble, please use the *eMZed group* at http://groups.google.com/group/emzed-users.





  

 


