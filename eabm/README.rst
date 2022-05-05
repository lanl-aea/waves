.. target-start-do-not-remove

.. _AEA Compute environment: https://aea.re-pages.lanl.gov/developer-operations/aea_compute_environment/release/aea_compute_environment.html
.. _ECMF: https://aea.re-pages.lanl.gov/python-projects/ecmf/main/
.. _Conda: https://docs.conda.io/en/latest/
.. _CMake: https://cmake.org/cmake/help/v3.14/
.. _ctest: https://cmake.org/cmake/help/latest/manual/ctest.1.html
.. _cmake-simulation: https://re-git.lanl.gov/kbrindley/cmake-simulation
.. _SCons: https://scons.org/
.. _SCons documentation: https://scons.org/documentation.html
.. _SCons-simulation: https://kbrindley.re-pages.lanl.gov/scons-simulation/main/
.. _SCons-simulation repository: https://re-git.lanl.gov/kbrindley/scons-simulation
.. _Scons-EABM: https://re-git.lanl.gov/kbrindley/scons-simulation/-/tree/dev/eabm

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
`SCons-simulation`_ collection of parametric study and simulation helper utilities. Besides the handful of command line
utilities, `SCons-simulation`_ also includes custom SCons builders that are commonly re-used in model simulation
(modsim) repositories. This EABM is used in the `SCons-simulation`_ tutorials as well as the `SCons-simulation
repository`_ integration and system tests.

.. project-description-end-do-not-remove

Documentation
=============

* Production version (``main`` branch): https://kbrindley.re-pages.lanl.gov/scons-simulation/main/scons-eabm/
* Development version (``dev`` branch): https://kbrindley.re-pages.lanl.gov/scons-simulation/dev/scons-eabm/

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
      path/to/local/git/clone/scons-simulation
      $ conda create --name scons-simulation-env --file environment.yml

2. Activate the environment

   .. code-block::

      $ conda activate scons-simulation-env

AEA server environments
=======================

A minimal environment for the scons-simulation project Gitlab-CI jobs is maintained on AEA servers.

1. Add the AEA modulefiles directory

   .. code-block::

      $ module use /projects/python/modulefiles

2. Load the project specific modulefile

   .. code-block::

      $ module load scons-simulation-env

.. env-end-do-not-remove

*****************
Build Simulations
*****************

.. build-start-do-not-remove

4. View the available targets (e.g. the simulations themselves and their intermediate build steps)

   .. code-block::

      $ WIP

5. Build all targets

   .. code-block::

      $ scons

6. Build a specific target

   .. code-block::

      $ scons <target name>

7. Remove the build target artifacts

   .. code-block::

      $ scons --clean

.. build-end-do-not-remove

*******
Testing
*******

.. test-start-do-not-remove

Unlike software projects, the primary model/simulation project tests are the successful completion of some subset of the
simulation targets. If the selected simulations run successfully, then the target passes. To facilitate Gitlab-CI
regression testing, the primary model/simluation targets have also been added as `SCons`_ tests. Secondary project tests
will use `SCons`_ for unit and integration testing project specific scripts, such as journal files and processing
scripts.

5. Build the required target(s). Test targets may not be part of the default target ``all``. If so, each target will
   need to be listed explicitly

   .. code-block::

      $ pwd
      path/to/local/git/clone/scons-simulation
      $ scons <target_1_name> <target-2_name>

6. Run all tests

   .. code-block::

      scons --keep-going

A full list of test names can be generated with the following command.

.. code-block::

   WIP

.. test-end-do-not-remove

*************
Documentation
*************

.. docs-start-do-not-remove

The documentation build is also automated with SCons as the ``documentation`` target.

5. Build the documentation target

   .. code-block::

      $ scons documentation

.. docs-end-do-not-remove
