.. target-start-do-not-remove

.. _AEA Compute environment: https://aea.re-pages.lanl.gov/developer-operations/aea_compute_environment/release/aea_compute_environment.html
.. _AEA Conda channel: https://aea.re-pages.lanl.gov/developer-operations/aea_compute_environment/aea-release/aea_compute_environment.html#aea-conda-channel
.. _ECMF: https://aea.re-pages.lanl.gov/python-projects/ecmf/main/
.. _Conda: https://docs.conda.io/en/latest/
.. _Conda installation: https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html
.. _Conda environment management: https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html
.. _CMake: https://cmake.org/cmake/help/v3.14/
.. _ctest: https://cmake.org/cmake/help/latest/manual/ctest.1.html
.. _cmake-simulation: https://re-git.lanl.gov/kbrindley/cmake-simulation
.. _SCons: https://scons.org/
.. _SCons documentation: https://scons.org/documentation.html
.. _SCons manpage: https://scons.org/doc/production/HTML/scons-man.html
.. _WAVES: https://kbrindley.re-pages.lanl.gov/waves/main/
.. _WAVES repository: https://re-git.lanl.gov/kbrindley/waves
.. _WAVES-EABM: https://re-git.lanl.gov/kbrindley/waves/-/tree/dev/eabm

.. _`Kyle Brindley`: kbrindley@lanl.gov
.. _`Thomas Roberts`: tproberts@lanl.gov
.. _`Sergio Cordova`: sergioc@lanl.gov
.. _`Prabhu Khalsa`: pkhalsa@lanl.gov
.. _`Scott Ouellette`: souellette@lanl.gov

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

* `Kyle Brindley`_
* `Prabhu Khalsa`_
* `Thomas Roberts`_
* `Sergio Cordova`_
* `Scott Ouellette`_

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
      $ conda create --name waves-env --file environment.txt --channel conda-forge

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

This project uses the `SCons`_ build system. This section will discuss some common build operations. For a full list of
`SCons`_ command line options and target build behavior, see the `SCons manpage`_. The `SCons manpage`_ is also
installed with `Scons`_ in the environment and can be opened from the command line as ``man scons`` in the `AEA Compute
environment`_. In local environments, the manpage may not be in the ``MANPATH``. You can find the manpage file and
make them available with something similar to any of the following, in increasing order of required background
knowledge.

.. code-block::

   # Find the scons manpage file
   $ find /path/to/local/environment -name scons.1
   /path/to/local/environment/bin/scons.1

   # Open manpage directly
   $ man /path/to/local/environment/bin/scons.1

   # Link SCons manpage to expected path and update MANPATH
   $ ln -s /path/to/local/environment/bin/scons.1 /path/to/local/environment/man/man1/scons.1
   $ export MANPATH=$MANPATH:/path/to/local/environment/man
   $ man scons

This project contains two, separate `SCons`_ project definitions, where the ``SConstruct`` file name indicates an
`SCons`_ project by convention. The WAVES package and documentation are defined in the ``waves/SConstruct`` file. The
WAVES-EABM stub and regression tests are defined in a separate ``waves/eabm/Sconstruct`` file. The following build
commands apply to each, but must be run from their respective project definition parent directories, ``waves`` and
``waves/eabm``. The available targets and aliases differ accordingly.

- View project specific command line options

  .. code-block::

     $ scons -h
     ...

- View the default targets and target aliases

  .. code-block::

     $ scons -h
     ...

- Build all default targets

  .. code-block::

     $ scons

- Build a specific target

  .. code-block::

     $ scons <target name>

- Remove the default targets' artifacts

  .. code-block::

     $ scons --clean

- Remove *all* targets' artifacts

  .. code-block::

     $ scons . --clean

.. build-end-do-not-remove

*******
Testing
*******

.. test-start-do-not-remove

This project uses the `SCons`_ build system. This section will discuss some common build operations. An abbreviated
options description can be displayed with ``scons -H``. For a full list of `SCons`_ command line options and target
build behavior, see the `SCons manpage`_. The `SCons manpage`_ is also installed with `Scons`_ in the environment and
can be opened from the command line as ``man scons`` in the `AEA Compute environment`_. In local environments, the
manpage may not be in the ``man`` program's search path, ``MANPATH``. You can find the manpage file and make them
available with something similar to any of the following, in increasing order of required background knowledge.

- Build the required target(s). Test targets may not be part of the default target list. If so, each target will
  need to be listed explicitly or the "all targets" character, ``.``, should be used to build *all* project targets.

  .. code-block::

     $ scons <target_1_name> <target-2_name>

- Run *all* simulation and test targets. Try to run all targets even if some fail.

  .. code-block::

     scons . --keep-going

A full list of test names can be generated with the following command.

.. code-block::

   WIP

.. test-end-do-not-remove

*************
Documentation
*************

.. docs-start-do-not-remove

The documentation build is also automated with SCons as the ``documentation`` target.

- Build the `WAVES`_ documentation

  .. code-block::

     $ pwd
     path/to/local/git/clone/waves/
     $ scons documentation

- Build the `WAVES-EABM`_ documentation

  .. code-block::

     $ pwd
     path/to/local/git/clone/waves/eabm
     $ scons documentation

.. docs-end-do-not-remove
