.. target-start-do-not-remove

.. _AEA Compute environment: https://aea.re-pages.lanl.gov/developer-operations/aea_compute_environment/release/aea_compute_environment.html
.. _ECMF: https://aea.re-pages.lanl.gov/python-projects/ecmf/main/
.. _Conda: https://docs.conda.io/en/latest/
.. _Conda installation: https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html
.. _Conda environment management: https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html
.. _CMake: https://cmake.org/cmake/help/v3.14/
.. _ctest: https://cmake.org/cmake/help/latest/manual/ctest.1.html
.. _cmake-simulation: https://re-git.lanl.gov/kbrindley/cmake-simulation
.. _SCons: https://scons.org/
.. _SCons documentation: https://scons.org/documentation.html
.. _WAVES: https://kbrindley.re-pages.lanl.gov/waves/main/
.. _WAVES repository: https://re-git.lanl.gov/kbrindley/waves
.. _WAVES-EABM: https://re-git.lanl.gov/kbrindley/waves/-/tree/dev/eabm

.. target-end-do-not-remove

#####
WAVES
#####

.. inclusion-marker-do-not-remove

***********
Description
***********

.. project-description-start-do-not-remove

A collection of parametric study and simulation helper utilities. Besides the handful of command line utilities,
`WAVES`_ also includes custom SCons builders that are commonly re-used in model simulation (modsim)
repositories. The simulations in this project use `SCons`_ as the automated build system. The `SCons documentation`_
covers build system concepts, command line options, and project definition.

This project includes a template `WAVES-EABM`_ which is used for the tutorials and for integration and regression
testing of the `WAVES`_ extensions to SCons.

.. project-description-end-do-not-remove

Documentation
=============

* Production version (``main`` branch): https://kbrindley.re-pages.lanl.gov/waves/main/
* Development version (``dev`` branch): https://kbrindley.re-pages.lanl.gov/waves/dev/

The `WAVES-EABM`_ documentation is hosted as a separate webpage as a demonstration for what EABM documentation can look
like.

* `WAVES-EABM`_ Production version (``main`` branch): https://kbrindley.re-pages.lanl.gov/waves/main/waves-eabm/
* `WAVES-EABM`_ Development version (``dev`` branch): https://kbrindley.re-pages.lanl.gov/waves/dev/waves-eabm/

Developers
==========

* Kyle Brindley: kbrindley@lanl.gov

********************
Activate Environment
********************

.. env-start-do-not-remove

Local environments
==================

`SCons`_ can be installed in a `Conda`_ environment with the `Conda`_ package manager. See the `Conda installation`_ and
`Conda environment management`_ documentation for more details about using `Conda`_.

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

      $ module use /projects/aea_compute/modulefiles

2. Load the project specific modulefile

   .. code-block::

      $ module load waves-env

.. env-end-do-not-remove

*****************
Build Simulations
*****************

.. build-start-do-not-remove

This project uses the `SCons`_ build system. This section will discuss some
common build operations. For a fulle list of `SCons`_ command line options and
target build behavior, see the `SCons manpage`_. The `SCons manpage`_ is also
installed with `Scons`_ in the environment and can be opened as ``man scons``
in the `AEA Compute environment`_. In local environments, the man pages may not
be in the ``MANPATH``. You can find the man pages file and make them available
with something similar to any of the following.

.. code-block::

   # Find the scons manpage file
   $ find /path/to/local/environment -name scons.1
   /path/to/local/environment/bin/scons.1

   # Open manpage directly
   $ man /path/to/local/environment/bin/scons.1

   # Link SCons manpage to expected location
   $ ln -s /path/to/local/environment/man/man1/scons.1 /path/to/local/environment/bin/scons.1
   $ man scons

   # Add path to MANPATH
   $ export MANPATH=$MANPATH:/path/to/local/environment/bin
   $ man scons

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

6. Build the `WAVES-EABM`_ documentation

   .. code-block::

      $ pwd
      path/to/local/git/clone/waves/eabm
      $ scons documentation

.. docs-end-do-not-remove
