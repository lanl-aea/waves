.. target-start-do-not-remove

.. _AEA Compute environment: https://aea.re-pages.lanl.gov/developer-operations/aea_compute_environment/release/aea_compute_environment.html
.. _Conda: https://docs.conda.io/en/latest/
.. _Conda installation: https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html
.. _Conda environment management: https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html
.. _SCons: https://scons.org/
.. _SCons documentation: https://scons.org/documentation.html
.. _SCons manpage: https://scons.org/doc/production/HTML/scons-man.html
.. _WAVES: https://aea.re-pages.lanl.gov/python-projects/waves/main/
.. _WAVES repository: https://re-git.lanl.gov/aea/python-projects/waves
.. _WAVES-EABM: https://re-git.lanl.gov/aea/python-projects/waves/-/tree/dev/quickstart
.. _WAVES-EABM documentation: https://aea.re-pages.lanl.gov/python-projects/waves/main/waves-eabm/

.. _`Kyle Brindley`: kbrindley@lanl.gov
.. _`Thomas Roberts`: tproberts@lanl.gov
.. _`Sergio Cordova`: sergioc@lanl.gov
.. _`Prabhu Khalsa`: pkhalsa@lanl.gov
.. _`Scott Ouellette`: souellette@lanl.gov
.. _`Matthew Fister`: mwfister@lanl.gov

.. target-end-do-not-remove

#####
WAVES
#####

.. inclusion-marker-do-not-remove

***********
Description
***********

.. project-description-start-do-not-remove

`WAVES`_ is a computational engineering workflow tool that integrates parametric studies with traditional software build systems.

In addition to the parametric study Python package and command line utilities, `WAVES`_ also includes `SCons`_ builders
for common engineering software used by model simulation (modsim) repositories. The tutorial simulations in this project
use `SCons`_ as the automated build system and translate software build system concepts in the language of engineering
simulation and analysis. The `SCons documentation`_ should be consulted as a reference for additional build system
concepts, command line options, and project configuration.

This project includes a template `WAVES-EABM`_ which is used for the tutorials and for integration and regression
testing of the `WAVES`_ extensions to SCons.

.. project-description-end-do-not-remove

Documentation
=============

The documentation is bundled with the Conda package and can be accessed locally without a network connection after
installation from the command line as ``waves docs``. The documentation is also web-hosted:

* Production version (``main`` branch): https://aea.re-pages.lanl.gov/python-projects/waves/main/
* Development version (``dev`` branch): https://aea.re-pages.lanl.gov/python-projects/waves/dev/

The `WAVES-EABM documentation`_ is hosted as a separate webpage as a demonstration for what EABM documentation can look
like.

* `WAVES-EABM`_ Production version (``main`` branch): https://aea.re-pages.lanl.gov/python-projects/waves/main/waves-eabm/
* `WAVES-EABM`_ Development version (``dev`` branch): https://aea.re-pages.lanl.gov/python-projects/waves/dev/waves-eabm/

Installation
============

.. installation-start-do-not-remove

This project is intended for deployment to ``conda-forge``. Until then, please contact the development team for a copy
of the most recent build. From an active Conda environment, the project can then be installed directly from the package
file as

.. code-block::

   $ conda install waves-*.tar.bz2

.. installation-end-do-not-remove

Developers
==========

* `Kyle Brindley`_
* `Prabhu Khalsa`_
* `Thomas Roberts`_
* `Sergio Cordova`_
* `Matthew Fister`_
* `Scott Ouellette`_

***************
Developer Notes
***************

Clone the project
=================

.. code-block::

   $ git clone ssh://git@re-git.lanl.gov:10022/aea/python-projects/waves.git

Symlinks
========

.. windows-notes-start-do-not-remove

This project uses symbolic links to minimize duplication of files where possible. Some files, such as the tutorial and
quickstart eabm package files, can not be shared in common due to their applications and the necessary directory
structure for each. However, if the file content is identical, a symbolic link is used to avoid duplicating the entire
file.

Symbolic links require special handling on Windows computers. If contributors are developing from a Windows machine,
they are encouraged to

1. Read about ``mklink`` and "developer mode" for Windows 10/11
2. Use an up-to-date version of git
3. Use one of the following git configurations

   .. code-block::

      # Global configuration. Run from anywhere.
      > git config --global core.symlinks true

      # Local configuration. Run from repository root directory after cloning.
      > git config core.symlinks true

4. Use unix line endings with one of the following git configurations

   .. code-block::

      # Global configuration. Run from anywhere.
      > git config --global core.autocrlf true

      # Local configuration. Run from repository root directory after cloning.
      > git config core.autocrlf true

.. windows-notes-end-do-not-remove

.. env-start-do-not-remove

Local development environments
==============================

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

AEA CI server environment
=========================

A minimal development environment for the waves project Gitlab-CI jobs is maintained on AEA servers.

1. Add the AEA modulefiles directory

   .. code-block::

      $ module use /projects/aea_compute/modulefiles

2. Load the project specific modulefile

   .. code-block::

      $ module load waves-env

.. env-end-do-not-remove

Build
=====

.. build-start-do-not-remove

To build the Conda package activate the development environment and run the conda (or mamba) build command found in the
CI configuration file. The current command may be found as

.. code-block::

   $ sed -n '/output_folder=/,/VERSION/p' .gitlab-ci.yml
   ...

.. code-block::

   $ output_folder='conda-build-artifacts'
   $ mkdir ${output_folder}
   $ VERSION=$(python -m setuptools_scm) mamba build recipe --channel conda-forge --no-anaconda-upload --croot /scratch/${USER}/conda-build --output-folder ${output_folder}

This project uses the `SCons`_ build system. This section will discuss some common build operations. For a full list of
`SCons`_ command line options and target build behavior, see the `SCons manpage`_. The `SCons manpage`_ is also
installed with `Scons`_ in the environment and can be opened from the command line as ``man scons`` in the `AEA Compute
environment`_. In local environments, the manpage may not be in the ``MANPATH``. You can find the manpage file and
make them available with something similar to any of the following, in increasing order of required background
knowledge.

.. code-block::

   # Activate the environment
   conda activate waves-env

   # Find the scons manpage file
   $ find $CONDA_PREFIX -name scons.1
   /path/to/waves-env/scons.1

   # Open manpage directly
   $ man $CONDA_PREFIX/scons.1

   # Link SCons manpage to expected path and update MANPATH
   $ ln -s $CONDA_PREFIX/scons.1 $CONDA_PREFIX/man/man1/scons.1
   $ export MANPATH=$MANPATH:$CONDA_PREFIX/man
   $ man scons

This project contains several, separate `SCons`_ project configurations, where the ``SConstruct`` file name indicates an
`SCons`_ project by convention. The WAVES package and documentation are defined in the ``waves/SConstruct`` file. The
WAVES-EABM modsim template and regression tests are defined in a separate ``waves/quickstart/Sconstruct`` file. The
WAVES tutorials each have a tutorial specific configuration file ``waves/tutorials/*SConstruct``. The following build
commands apply to each, but must be run from their respective project configuration parent directories, ``waves``,
``waves/quickstart`` and ``waves/tutorials``. The available targets and aliases differ accordingly.

When executing the tutorials or quickstart build commands directly in the repository, the WAVES project root repository
must be put on ``PYTHONPATH``. In personal (*but not shared*) virtual environments, the preferred method is to run
``conda develop .`` once from the project root directory. See the `Conda`_ documentation for more information about
"development" mode installs. For shared environments, the preferred solution is to prefix the following commands with
``PYTHONPATH=.. ``, where it is assumed that the ``PWD`` is the tutorial or quickstart root directory.

- View project specific command line options, default targets, and aliases

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

Test
====

.. test-start-do-not-remove

Unlike software projects, the primary model/simulation project tests are the successful completion of some subset of the
simulation targets. If the selected simulations run successfully, then the target passes. Secondary project tests will
use `SCons`_ to execute unit and integration testing for project specific scripts, such as journal files and Python
processing scripts.

- Build the required target(s). Test targets may not be part of the default target list. If so, each target will
  need to be listed explicitly or the "all targets" character, ``.``, should be used to build *all* project targets.

  .. code-block::

     $ scons <target_1_name> <target-2_name>

- Run *all* simulation and test targets. Try to run all targets even if some fail.

  .. code-block::

     scons . --keep-going

The full list of continuous integration test targets can be found in the Gitlab-CI file, ``.gitlab-ci.yml``.

.. code-block::

   $ pwd
   path/to/local/git/clone/waves/
   $ sed -n '/fast-test/,/tags/p' .gitlab-ci.yml

.. test-end-do-not-remove

Documentation
=============

.. docs-start-do-not-remove

The documentation build is also automated with SCons as the ``documentation`` target.

- Build the `WAVES`_ documentation

  .. code-block::

     $ pwd
     path/to/local/git/clone/waves/
     $ scons documentation

- Build the `WAVES-EABM`_ documentation. The WAVES package must be on ``PYTHONPATH``. For developers, the least
  disruptive solution is a per-command modification of ``PYTHONPATH``.

  .. code-block::

     $ pwd
     path/to/local/git/clone/waves/eabm
     $ PYTHONPATH=/path/to/local/git/clone/waves:$PYTHONPATH scons documentation

.. docs-end-do-not-remove
