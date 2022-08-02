######################
Command Line Utilities
######################

******************************
|PROJECT| Command Line Utility
******************************

The |PROJECT| command line utility proves some basic functionality by calling ``waves`` from the command line.

.. argparse::
   :ref: waves.waves.get_parser

***********************
|PROJECT| Build Wrapper
***********************

|PROJECT| provides a build wrapper for the model repository `SCons`_ configuration build process. The build wrapper
creates a new, unique build directory for every build execution.

Optionally, the build wrapper will create a model repository clone in the build directory to separate the original
repository's source files from that of the build directory. This is useful for launching builds while continuing
development efforts in the original repositoy that would otherwise produce ambiguous build states.

The build wrapper command line options and behavior are described in the help message as

.. literalinclude:: waves_build_wrapper_message.txt

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
