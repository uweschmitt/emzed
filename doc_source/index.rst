.. documentation master file, created by
   sphinx-quickstart on Fri Oct 28 14:45:49 2011.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

mzExplore documentation
=======================

Contents:

.. toctree::
   :maxdepth: 2

   tutorial
   

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

============
Introduction
============

*mzExplore* is a framework for anaylising and processing LCMS data.
This is a short overview and tutorial of the capabilites of this framework.

The framework was developed with several ideas in mind:

* Current frameworks and software are located on one of the following extremes:
        
 * Fast and flexible frameworks, but in languages as C++ which only
   can be used by experienced programmers. Further playing with new
   ideas for analyzing data is hard due to the programming effort
   and slow edit-compile cylcles.

 * Closed black box solutions with graphical user interfaces. These
   are easy to use, but not flexible at all.  

 Our goal was to combine the positive aspects of both extremes: an easy to
 learn framework which is flexible and allows inspection and analysis of
 data either interactive or by easy to write Python scripts.

 This is one of the reasons why we choose Python.
	
* The invention of workspace providing software as *Matlab* and *R* really
  leveraged the productivity of mathematicians and other scientists.
  We try to introduce this concept for analyizing LCMS data.

* Instead of reinventing the wheel we cherry picked algorithms from other
  frameworks and libraries. In the current version we use routines from
  `open-ms <http://open-ms.de>`_  and `xcms <http://xcms.metlin.org>`_

* In order to avoid imports and export to other software, we try to integrate
  all needed functionality in one framework.


Features
========

The framework provides several functionalities:

1. Processing of Peak-Maps:

   * Load and store of data in several file formats as mzXML, mzML and mzData.

   * Conversion from raw gaussian data to centroided data

   * Interactive and graphical inspection of peakmaps 

   * Extraction of features (mass traces) from peakmaps

2. Processing of features and feature sets:

   * mz-Alignment against arbitrary universal metabolites or marker substances.

   * Retention time alignment of feature sets.

   * Quantitative Analysis of chromatographic peaks, integration of peaks, fitting of assymetric, non-gaussian peaks.

   * Features are kept in a datastructure called ``Table`` which is very powrfull and allows SQL like operations. 

   * Matching of features against the `PubChem <http://x.org>`_ database or the `Metlin <http://x.org>`_ service.

   * Matching against isotope patterns of arbitrary molecules and arbitrary isotope abundances.

   * Interactive inspection of Feature sets and the underlying peak maps.

   * Interactive editing of ``Table`` objects.

3. Usefull helpers:

   * Easy building of dialogs for input forms.

   * Easy access to element data as masses and abundances.

   * Computation of isotope patterns of arbitrary molecules.

