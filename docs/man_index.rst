#########
|project|
#########

********
Synopsis
********

.. argparse::
   :ref: waves.main.get_parser
   :nodefault:
   :nosubcommands:

***********
Description
***********

.. include:: project_brief.txt

*********************
|PROJECT| Subcommands
*********************
****
docs
****

.. argparse::
   :ref: waves.main.get_parser
   :nodefault:
   :path: docs

.. _waves_fetch_cli:

*********************
|PROJECT| Subcommands
*********************
*****
fetch
*****

.. argparse::
   :ref: waves.main.get_parser
   :nodefault:
   :path: fetch

.. _waves_quickstart_cli:

*********************
|PROJECT| Subcommands
*********************
**********
quickstart
**********

.. argparse::
   :ref: waves.main.get_parser
   :nodefault:
   :path: quickstart

.. _waves_build_cli:

*********************
|PROJECT| Subcommands
*********************
*****
build
*****

.. argparse::
   :ref: waves.main.get_parser
   :nodefault:
   :path: build

******************
Python Package API
******************
**************
SCons Builders
**************

.. automodule:: waves.builders
    :members:
    :show-inheritance:
    :synopsis: WAVES Analysis for Verified Engineering Simulations SCons builder extensions

******************
Python Package API
******************
********************
Parameter Generators
********************

.. automodule:: waves.parameter_generators
    :members:
    :show-inheritance:
    :synopsis: A collection of Python based parameter study generators

****************
Bundled commands
****************
.. _odb_extract_cli:

***********
ODB Extract
***********

.. argparse::
   :ref: waves.abaqus.odb_extract.get_parser

****************
Bundled commands
****************
***************
Parameter Study
***************

.. argparse::
   :ref: waves.parameter_study.get_parser
   :nodefault:
