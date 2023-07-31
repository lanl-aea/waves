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

.. _waves_visualize_cli:

*********************
|PROJECT| Subcommands
*********************
*********
visualize
*********

.. argparse::
   :ref: waves.main.get_parser
   :nodefault:
   :path: visualize

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

.. _waves_cartesian_product_cli:

*********************
|PROJECT| Subcommands
*********************
*****************
cartesian_product
*****************

.. argparse::
   :ref: waves.main.get_parser
   :nodefault:
   :path: cartesian_product

.. _waves_custom_study_cli:

*********************
|PROJECT| Subcommands
*********************
************
custom_study
************

.. argparse::
   :ref: waves.main.get_parser
   :nodefault:
   :path: custom_study

.. _waves_latin_hypercube_cli:

*********************
|PROJECT| Subcommands
*********************
***************
latin_hypercube
***************

.. argparse::
   :ref: waves.main.get_parser
   :nodefault:
   :path: latin_hypercube

.. _waves_sobol_sequence_cli:

*********************
|PROJECT| Subcommands
*********************
**************
sobol_sequence
**************

.. argparse::
   :ref: waves.main.get_parser
   :nodefault:
   :path: sobol_sequence

******************
Python Package API
******************
**************
SCons Builders
**************

.. automodule:: waves.scons_extensions
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
