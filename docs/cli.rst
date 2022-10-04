######################
Command Line Utilities
######################

.. _waves_cli:

******************************
|project| Command Line Utility
******************************

The |PROJECT| command line utility provides access to bundled HTML documentation, meta information about the |PROJECT|
Conda package, a quickstart modsim template, and a thin `SCons`_ build wrapper.

.. argparse::
   :ref: waves.waves.get_parser
   :nodefault:
   :nosubcommands:

docs
====

.. argparse::
   :ref: waves.waves.get_parser
   :nodefault:
   :path: docs

.. _waves_quickstart_cli:

quickstart
==========

.. argparse::
   :ref: waves.waves.get_parser
   :nodefault:
   :path: quickstart

.. _waves_build_cli:

build
=====

.. argparse::
   :ref: waves.waves.get_parser
   :nodefault:
   :path: build

.. _parameter_study_cli:

***************
Parameter Study
***************

.. argparse::
   :ref: waves.parameter_study.get_parser
   :nodefault:
   :nosubcommands:

cartesian_product
=================

.. argparse::
   :ref: waves.parameter_study.get_parser
   :nodefault:
   :path: cartesian_product

custom_study
============

.. argparse::
   :ref: waves.parameter_study.get_parser
   :nodefault:
   :path: custom_study

latin_hypercube
===============

.. argparse::
   :ref: waves.parameter_study.get_parser
   :nodefault:
   :path: latin_hypercube 

sobol_sequence
==============

.. argparse::
   :ref: waves.parameter_study.get_parser
   :nodefault:
   :path: sobol_sequence 

.. _odb_extract_cli:

***********
ODB Extract
***********

.. argparse::
   :ref: waves.abaqus.odb_extract.get_parser

*********
Sta Parse
*********

.. argparse::
   :ref: waves.abaqus.sta_parse.get_parser

*********
Msg Parse
*********

.. argparse::
   :ref: waves.abaqus.msg_parse.get_parser
