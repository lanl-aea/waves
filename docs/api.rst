###
API
###

.. _waves_builders_api:

**************
SCons Builders
**************

.. automodule:: waves.builders
    :members:
    :show-inheritance:
    :synopsis: WAVES Analysis for Validated Engineering Simulations SCons builder extensions

.. _parameter_generator_api:

********************
Parameter Generators
********************

.. automodule:: waves.parameter_generators
    :members:
    :show-inheritance:
    :synopsis: A collection of Python based parameter study generators

**********************
Odb Report File Parser
**********************

.. automodule:: waves.abaqus.abaqus_file_parser.OdbReportFileParser
    :members:
    :show-inheritance:
    :synopsis: Parses an odbreport file produced by Abaqus

***************
Sta File Parser
***************

.. automodule:: waves.abaqus.abaqus_file_parser.StaFileParser
    :members:
    :show-inheritance:
    :synopsis: Parses an sta file produced by Abaqus

***************
Msg File Parser
***************

.. automodule:: waves.abaqus.abaqus_file_parser.MsgFileParser
    :members:
    :show-inheritance:
    :synopsis: Parses a msg file produced by Abaqus

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
   :language: bash
