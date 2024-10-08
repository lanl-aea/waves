.. _devops_manual:

################
Developer Manual
################

*****
Clone
*****

.. include:: README.txt
   :start-after: clone-start-do-not-remove
   :end-before: clone-end-do-not-remove

.. include:: dependencies.txt

********************
Activate Environment
********************

Local development environments
==============================

.. include:: README.txt
   :start-after: env-start-do-not-remove
   :end-before: env-end-do-not-remove

AEA CI server environment
=========================

A minimal development environment for the waves project Gitlab-CI jobs is maintained on AEA servers.

1. Add the AEA modulefiles directory

   .. code-block::

      $ module use /projects/aea_compute/modulefiles

2. Load the project specific modulefile

   .. code-block::

      $ module load waves-env

The Conda packages found in ``environment.yml`` are reproduced in the :ref:`modsim_dependencies` section.

HPC CI server environment
=========================

.. warning::

   While the system tests are run with an HPC CI job, the machine and runner uptime and system test runtime are
   considered too fragile for reliable use. The AEA RHEL system tests pass in less than 8 minutes, but the HPC system
   test job has been observed to time out after an hour. The HPC CI system tests are always run for merge-requests and
   schedule pipelines, but the pass/fail status is not used to mark CI jobs as failing. Developers are encourage to
   check the HPC system test results, but not required to address failing HPC CI jobs.

   There are four known HPC CI system test failures

   * (2) Cubit tutorial and alternate (Sierra or HPC Sierra installation bug)
   * (1) Quinoa tutorial (Reason unknown. Direct, manual tutorial execution performs as expected)
   * (1) Abaqus Sbatch tutorial (Reason unknown. Direct, manual tutorial execution performs as expected)

   Occasionally, running the HPC system tests manually will reproduce a superset of known failures. Most often, the
   ModSim templates fail, despite performing as expected in direct, manual execution.

For computing policy reasons, HPC CI jobs are owned by the launching user and launched with the user's account. The HPC
CI server environment must be created in the launching user's scratch space. For merge request pipelines, this means a
project development environment will be created in the submitting developer's scratch space, e.g.
``${system_scratch}/$USER/waves-env``.

Because the CI job runs as the launching user, Conda will create a package and environment cache according to the user's
HPC Conda configuration. By default, Conda creates ``~/.conda/pkgs`` for the package cache, which can grow quite
large. If a user's home directory space is limited, developers are highly encouraged to configure Conda to use their
scratch space for the package cache, e.g. with a ``~/.condarc`` file using the template below, where the text
``${user_scratch}`` is replaced by the absolute path to the user's scratch directory.

.. code-block::

   envs_dirs:
     - ${user_scratch}/conda/envs

   pkgs_dirs:
     - ${user_scratch}/conda/pkgs

You can read more about managing the Conda package and environment cache configuration here:
https://conda.io/projects/conda/en/latest/user-guide/configuration/custom-env-and-pkg-locations.html

.. include:: contribution.txt

.. _build:

*****
Build
*****

To build the Conda package activate the development environment and run the conda build command found in the
CI configuration file. The current command may be found as

.. code-block::

   $ sed -n '/output_folder=/,/VERSION/p' .gitlab-ci.yml
   ...

.. code-block::

   $ output_folder='conda-bld'
   $ mkdir ${output_folder}
   $ VERSION=$(python -m setuptools_scm) conda build recipe --channel conda-forge --no-anaconda-upload --croot /scratch/${USER}/conda-build --output-folder ${output_folder}

A second recipe that bundles the LANL internally linked documentation is found in ``waves/recipe-internal`` and can be
built similarly by replacing ``recipe`` with ``recipe-internal`` in the above command.

This project uses the `SCons`_ build system. This section will discuss some common build operations. For a full list of
`SCons`_ command-line options and target build behavior, see the `SCons manpage`_. The `SCons manpage`_ is also
installed with `Scons`_ in the environment and can be opened from the command-line as ``man scons`` in the `AEA Compute
environment`_. In local environments, the manpage may not be in the ``MANPATH``. You can find the manpage file and
make them available with something similar to any of the following, in increasing order of required background
knowledge.

.. code-block::

   # Activate the environment
   $ conda activate waves-env

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
modsim template and regression tests are defined in a separate ``waves/modsim_template/Sconstruct`` file. The WAVES
tutorials each have a tutorial specific configuration file ``waves/tutorials/*SConstruct``. The following build commands
apply to each, but must be run from their respective project configuration parent directories, ``waves``,
``waves/modsim_template`` and ``waves/tutorials``. The available targets and aliases differ accordingly.

When executing the tutorials or modsim template build commands directly in the repository, the WAVES project root
repository must be put on ``PYTHONPATH``. In personal (*but not shared*) virtual environments, the preferred method is
to run ``conda develop .`` once from the project root directory. See the `Conda`_ documentation for more information
about "development" mode installs. For shared environments, the preferred solution is to prefix the following commands
with ``PYTHONPATH=.. ``, where it is assumed that the ``PWD`` is the tutorial or modsim template root directory.

- View project specific command-line options, default targets, and aliases

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

****
Test
****

The project regression suite is collected under the ``regression`` alias and can be run as

.. code-block::

   $ scons regression

The continuous integration server also performs a separate style guide check using ``flake8`` and associated alias

.. code-block::

   $ scons flake8

WAVES has dedicated target aliases for the unit and system tests. To run the unit tests, activate a conda environment
and run

.. code-block::

   $ scons pytest

The tutorials and modsim template are run as system tests and require third-party software not available on conda-forge.
To run the system tests, install the third-party software and make them available in your ``PATH``, activate a conda
environment and run

.. code-block::

   $ scons systemtest

The full list of continuous integration test commands can be found in the Gitlab-CI file, ``.gitlab-ci.yml``.

.. code-block::

   $ pwd
   path/to/local/git/clone/waves/
   $ sed -n '/fast-test/,/tags/p' .gitlab-ci.yml

The WAVES unit and system tests may also be executed from the installation directory. These tests use pytest directly
and may require non-default pytest options and markers to execute the system tests serially. The full list of CI
commands may be found in the internal recipe file, ``recipe-internal/meta.yaml``, under the ``test`` keyword. The
following grep command will show the pytest commands and options.

.. code-block::

   $ grep "pytest " recipe-internal/*

Test Local Module
=================

When testing CLI changes locally, the waves module must be run as a script. We must also set the ``PYTHONPATH``
in order to include the current waves module when operating on a configuration that imports waves.

Below is an example of a visualization test of an SConstruct file using the local waves module.

.. code-block::

   $ pwd
   path/to/local/git/clone/waves/
   $ PYTHONPATH=$PWD python -m waves._main visualize . --sconstruct /path/to/local/SConstruct

*************
Documentation
*************

.. include:: README.txt
   :start-after: docs-start-do-not-remove
   :end-before: docs-end-do-not-remove

- Build the `MODSIM-TEMPLATE`_ documentation. The WAVES package must be on ``PYTHONPATH``. For developers, the least
  disruptive solution is a per-command modification of ``PYTHONPATH``.

  .. code-block::

     $ pwd
     path/to/local/git/clone/waves/modsim_template
     $ PYTHONPATH=/path/to/local/git/clone/waves:$PYTHONPATH scons documentation

*************
Windows users
*************

This project uses symbolic links to minimize duplication of files where possible. Some files, such as the tutorial and
modsim template package files, can not be shared in common due to their applications and the necessary directory
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
