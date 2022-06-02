######################
Command Line Utilities
######################

*************
Build wrapper
*************

The build system provides a build wrapper for the model repository CMake configuration build process. The build wrapper
creates a new, unique build directory for every build execution.

Optionally, the build wrapper will create a model repository clone in the build directory to separate the original
repository's source files from that of the build directory. This is useful for launching builds while continuing
development efforts in the original repositoy that would otherwise produce ambiguous build states.

The build wrapper command line options and behavior are described in the help message as

.. .. literalinclude:: build_wrapper_message.txt
..    :language: bash

.. _abaqus_wrapper:

**************
Abaqus wrapper
**************

This project contains a thin wrapper around Abaqus that provides

1. Non-zero exit codes for failed simulations
2. Interactive output redirect to a log file

Both features are required when executing Abaqus from a build system to allow the build system to exit a workflow after
a failed simulation and provide robust wait criteria to determine target completion.

The abaqus wrapper command line options and behavior are described in the usage message as

.. literalinclude:: abaqus_wrapper_message.txt
   :language: bash

***************
Parameter Study
***************

.. argparse::
   :ref: waves.parameter_study.get_parser

***********
ODB Extract
***********

.. argparse::
   :ref: waves.abaqus.command_line_tools.odb_extract.get_parser
