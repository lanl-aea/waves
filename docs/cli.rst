######################
Command Line Utilities
######################

.. _waves_cli:

******************************
|PROJECT| Command Line Utility
******************************

The |PROJECT| command line utility provides access to bundled HTML documentation, meta information about the |PROJECT|
Conda package, and a thin `SCons`_ build wrapper.

.. argparse::
   :ref: waves.waves.get_parser

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
