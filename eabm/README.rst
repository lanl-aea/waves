.. target-start-do-not-remove

.. _AEA Compute environment: https://aea.re-pages.lanl.gov/developer-operations/aea_compute_environment/release/aea_compute_environment.html
.. _ECMF: https://aea.re-pages.lanl.gov/python-projects/ecmf/main/
.. _Conda: https://docs.conda.io/en/latest/
.. _CMake: https://cmake.org/cmake/help/v3.14/
.. _ctest: https://cmake.org/cmake/help/latest/manual/ctest.1.html
.. _cmake-simulation: https://re-git.lanl.gov/kbrindley/cmake-simulation
.. _SCons: https://scons.org/
.. _SCons documentation: https://scons.org/documentation.html
.. _WAVES: https://kbrindley.re-pages.lanl.gov/waves/main/
.. _WAVES repository: https://re-git.lanl.gov/kbrindley/waves
.. _Scons-EABM: https://re-git.lanl.gov/kbrindley/waves/-/tree/dev/eabm

.. target-end-do-not-remove

##########
SCons-EABM
##########

.. inclusion-marker-do-not-remove

***********
Description
***********

.. project-description-start-do-not-remove

The `SCons-EABM`_ contains the demonstration engineering analysis baseline model (EABM) that matches the
`WAVES`_ collection of parametric study and simulation helper utilities. Besides the handful of command line
utilities, `WAVES`_ also includes custom SCons builders that are commonly re-used in model simulation
(modsim) repositories. This EABM is used in the `WAVES`_ tutorials as well as the `WAVES
repository`_ integration and system tests.

.. project-description-end-do-not-remove

Documentation
=============

* Production version (``main`` branch): https://kbrindley.re-pages.lanl.gov/waves/main/scons-eabm/
* Development version (``dev`` branch): https://kbrindley.re-pages.lanl.gov/waves/dev/scons-eabm/

Developers
==========

* Kyle Brindley: kbrindley@lanl.gov

********************
Activate Environment
********************

.. env-start-do-not-remove

Local environments
==================

`SCons`_ can be installed in a `Conda`_ environment with the `Conda`_ package manager.

1. Create the environment if it doesn't exist

   .. code-block::

      $ pwd
      path/to/local/git/clone/waves
      $ conda create --name waves-env --file environment.yml

2. Activate the environment

   .. code-block::

      $ conda activate waves-env

AEA server environments
=======================

A minimal environment for the waves project Gitlab-CI jobs is maintained on AEA servers.

1. Add the AEA modulefiles directory

   .. code-block::

      $ module use /projects/python/modulefiles

2. Load the project specific modulefile

   .. code-block::

      $ module load waves-env

.. env-end-do-not-remove

*****************
Build Simulations
*****************

.. build-start-do-not-remove

3. View project specific command line options

   .. code-block::

      $ scons -h
      ...

This project limits the default target list to the documentation with the `SCons`_ ``Default`` command. Simulation
targets must be specified directly on the command line. The `SCons`_ "all targets" character, ``.``, may also be
specified to build every target in the repository, including *all* simulation targets. Simulation targets may be
specified by output file name or by target alias, which is set to match the parent directory for the target
configuration, e.g. ``tutorial_01_geometry``.

4. View the default targets and target aliases

   .. code-block::

      $ pwd
      path/to/local/git/clone/waves/eabm
      $ scons -h
      ...

5. Build default targets

   .. code-block::

      $ scons

6. Build *all* targets

   .. code-block::

      $ scons .

7. Build a specific target

   .. code-block::

      $ scons <target name>

8. Remove *all* build target artifacts

   .. code-block::

      $ scons . --clean

.. build-end-do-not-remove

*******
Testing
*******

.. test-start-do-not-remove

Unlike software projects, the primary model/simulation project tests are the successful completion of some subset of the
simulation targets. If the selected simulations run successfully, then the target passes. Secondary project tests will
use `SCons`_ to execute unit and integration testing for project specific scripts, such as journal files and Python
processing scripts.

5. Build the required target(s). Test targets may not be part of the default target list. If so, each target will
   need to be listed explicitly or the "all targets" character, ``.``, should be used to build *all* project targets.

   .. code-block::

      $ pwd
      path/to/local/git/clone/waves
      $ scons <target_1_name> <target-2_name>

6. Run *all* simulation and test targets. Try to run all targets even if some fail.

   .. code-block::

      scons . --keep-going

.. test-end-do-not-remove

*************
Documentation
*************

.. docs-start-do-not-remove

The documentation build is also automated with SCons as the ``documentation`` target alias.

5. Build the documentation target

   .. code-block::

      $ scons documentation

.. docs-end-do-not-remove
