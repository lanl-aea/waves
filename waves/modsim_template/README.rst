.. target-start-do-not-remove

.. _AEA Compute environment: https://aea.re-pages.lanl.gov/developer-operations/aea_compute_environment/aea_compute_environment.html
.. _Conda: https://docs.conda.io/en/latest/
.. _Conda installation: https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html
.. _Conda environment management: https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html
.. _SCons: https://scons.org/
.. _SCons documentation: https://scons.org/documentation.html
.. _SCons manpage: https://scons.org/doc/production/HTML/scons-man.html
.. _WAVES: https://lanl-aea.github.io/waves/index.html
.. _MODSIM-TEMPLATE: https://github.com/lanl-aea/waves/tree/main/waves/modsim_template
.. _MODSIM-TEMPLATE documentation: https://aea.re-pages.lanl.gov/python-projects/waves/modsim-template/

.. _`Kyle Brindley`: kbrindley@lanl.gov
.. _`Thomas Roberts`: tproberts@lanl.gov
.. _`Sergio Cordova`: sergioc@lanl.gov
.. _`Prabhu Khalsa`: pkhalsa@lanl.gov
.. _`Scott Ouellette`: souellette@lanl.gov
.. _`Matthew Fister`: mwfister@lanl.gov
.. _`Chris Johnson`: clj@lanl.gov

.. target-end-do-not-remove

###############
MODSIM-TEMPLATE
###############

.. inclusion-marker-do-not-remove

***********
Description
***********

.. project-description-start-do-not-remove

This project uses the `WAVES`_ collection of parametric study and simulation helper utilities. This project was
generated from the `WAVES`_ ``fetch`` subcommand and `MODSIM-TEMPLATE`_.

.. project-description-end-do-not-remove

Documentation
=============

* GitHub: https://lanl-aea.github.io/waves/modsim-template/index.html
* LANL: https://aea.re-pages.lanl.gov/python-projects/waves/modsim-template/

Developers
==========

* `Kyle Brindley`_
* `Prabhu Khalsa`_
* `Thomas Roberts`_
* `Sergio Cordova`_
* `Matthew Fister`_
* `Scott Ouellette`_

********************
Activate Environment
********************

.. env-start-do-not-remove

AEA server environments
=======================

A shared `AEA Compute environment`_ is maintained on AEA servers. See the `AEA Compute environment`_ documentation for
the official use and activation instructions. A minimal activation description is included below for convenience.

1. Add the AEA modulefiles directory

   .. code-block::

      $ module use /projects/aea_compute/modulefiles

2. Load the shared environment modulefile

   .. code-block::

      $ module load aea-release

Local environments
==================

`SCons`_ and `WAVES`_ can be installed in a `Conda`_ environment with the `Conda`_ package manager. See the `Conda
installation`_ and `Conda environment management`_ documentation for more details about using `Conda`_.

1. Create the environment if it doesn't exist

   .. code-block::

      $ conda env create --name modsim-template-env --file environment.yml

2. Activate the environment

   .. code-block::

      $ conda activate modsim-template-env

.. env-end-do-not-remove

*****************
Build Simulations
*****************

.. build-start-do-not-remove

This project uses the `SCons`_ build system. This section will discuss some common build operations. An abbreviated
options description can be displayed with ``scons -H``. For a full list of `SCons`_ command line options and target
build behavior, see the `SCons manpage`_. The `SCons manpage`_ is also installed with `Scons`_ in the environment and
can be opened from the command line as ``man scons``

- View project specific command line options

  .. code-block::

     $ scons -h
     ...

This project limits the default target list to the documentation with the `SCons`_ ``Default`` command. Simulation
targets must be specified directly on the command line. The `SCons`_ "all targets" character, ``.``, may also be
specified to build every target in the repository, including *all* simulation targets. Simulation targets may be
specified by output file name or by target alias, which is set to match the parent directory for the target
configuration, e.g. ``tutorial_01_geometry``.

- View the default targets and target aliases

  .. code-block::

     $ scons -h
     ...

- Build default targets

  .. code-block::

     $ scons

- Build *all* targets

  .. code-block::

     $ scons .

- Build a specific target

  .. code-block::

     $ scons <target name>

- Remove *all* build target artifacts

  .. code-block::

     $ scons . --clean

- For debugging workflows, use the verbose output option of SCons

  .. code-block:: bash

     $ scons target --debug=explain

Because `SCons`_ uses Python as a scripting language, the usual Python debugging techniques may be placed directly in
the configuration file, as well: https://docs.python.org/3/library/pdb.html.

.. build-end-do-not-remove

*******
Testing
*******

.. test-start-do-not-remove

Unlike software projects, the primary model/simulation project tests are the successful completion of some subset of the
simulation targets. If the selected simulations run successfully, then the target passes. Secondary project tests will
use `SCons`_ to execute unit and integration testing for project specific scripts, such as journal files and Python
processing scripts.

In this project, the regression test suite includes simulation datachecks, documentation builds, and unit testing. For
convenience, the regression suite workflows are collected under the ``regression`` alias.

- Run the regression tests

  .. code-block::

     $ scons regression

- Run *all* simulation and test targets. Try to run all targets even if some fail.

  .. code-block::

     scons regression --keep-going

.. test-end-do-not-remove

*************
Documentation
*************

.. docs-start-do-not-remove

The documentation build is also automated with SCons as the ``documentation`` target alias.

- Build all documentation targets

  .. code-block::

     $ scons documentation

- Build the HTML documentation

  .. code-block::

     $ scons html

.. docs-end-do-not-remove
