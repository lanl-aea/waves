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

#####
WAVES
#####

.. inclusion-marker-do-not-remove

***********
Description
***********

.. project-description-start-do-not-remove

Testing `SCons`_ as a build system for simulations. Evaluating `SCons`_ features and behavior against `CMake`_ and `ECMF`_
features and behavior. The related `cmake-simulation`_ project established the feasibility of using a build system like
`CMake`_ in place of the `ECMF`_.

A collection of parametric study and simulation helper utilities. Besides the handful of command line utilities,
`WAVES`_ also includes custom SCons builders that are commonly re-used in model simulation (modsim)
repositories. The simulations in this project use `SCons`_ as the automated build system. The `SCons documentation`_
covers build system concepts, command line options, and project definition.

This project includes a template `SCons-EABM`_ which is used for the tutorials and for integration and regression
testing of the `WAVES`_ extensions to SCons.

.. project-description-end-do-not-remove

Documentation
=============

* Production version (``main`` branch): https://kbrindley.re-pages.lanl.gov/waves/main/
* Development version (``dev`` branch): https://kbrindley.re-pages.lanl.gov/waves/dev/

The `SCons-EABM`_ documentation is hosted as a separate webpage as a demonstration for what EABM documentation can look
like.

* `SCons-EABM`_ Production version (``main`` branch): https://kbrindley.re-pages.lanl.gov/waves/main/scons-eabm/
* `SCons-EABM`_ Development version (``dev`` branch): https://kbrindley.re-pages.lanl.gov/waves/dev/scons-eabm/

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

4. View the default targets and target aliases

   .. code-block::

      $ pwd
      path/to/local/git/clone/waves/
      $ scons -h
      ...

      $ cd eabm
      $ pwd
      path/to/local/git/clone/waves/eabm
      $ scons -h
      ...

5. Build all default targets

   .. code-block::

      $ pwd
      path/to/local/git/clone/waves/eabm
      $ scons

6. Build a specific target

   .. code-block::

      $ pwd
      path/to/local/git/clone/waves/eabm
      $ scons <target name>

7. Remove the default targets' artifacts

   .. code-block::

      $ pwd
      path/to/local/git/clone/waves/eabm
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
      path/to/local/git/clone/waves/eabm
      $ scons <target_1_name> <target-2_name>

6. Run all tests

   .. code-block::

      $ pwd
      path/to/local/git/clone/waves/eabm
      WIP

A full list of test names can be generated with the following command.

.. code-block::

   WIP

.. test-end-do-not-remove

*************
Documentation
*************

.. docs-start-do-not-remove

The documentation build is also automated with SCons as the ``documentation`` target.

5. Build the `WAVES`_ documentation

   .. code-block::

      $ pwd
      path/to/local/git/clone/waves/
      $ scons documentation

6. Build the `SCons-EABM`_ documentation

   .. code-block::

      $ pwd
      path/to/local/git/clone/waves/eabm
      $ scons documentation

.. docs-end-do-not-remove
