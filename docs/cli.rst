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
   :nosubcommands:

docs
====

.. argparse::
   :ref: waves.waves.get_parser
   :path: docs

.. _waves_quickstart_cli:

quickstart
==========

.. argparse::
   :ref: waves.waves.get_parser
   :path: quickstart

.. _waves_build_cli:

build
=====

.. argparse::
   :ref: waves.waves.get_parser
   :path: build

.. _parameter_study_cli:

***************
Parameter Study
***************

.. argparse::
   :ref: waves.parameter_study.get_parser

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
