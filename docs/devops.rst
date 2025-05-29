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

The Conda packages found in ``environment.yml`` are reproduced in the :ref:`modsim_dependencies` section.

Local development environments
==============================

.. include:: README.txt
   :start-after: env-start-do-not-remove
   :end-before: env-end-do-not-remove

AEA CI server environment
=========================

The AEA CI server environment is created under the default Gitlab-Runner user in the Gitlab-Runner build directory and
is not available for developers. The AEA CI jobs use a mix of the ``environment.yml``, ``conda-build.yml``, and
``pip-build.yml`` files. AEA RHEL developers may use the full ``environment.yml`` file to create a local development
environment that closely mirrors the linux CI environment.

By default, Conda creates ``~/.conda/pkgs`` for the package cache, which can grow quite
large. If a user's home directory space is limited, developers are highly encouraged to configure Conda to use their
projects space for the package cache, e.g. with a ``~/.condarc`` file using the template below, where the text
``${user}`` is replaced by the user name.

.. code-block::

   envs_dirs:
     - /projects/${user}/conda/envs

   pkgs_dirs:
     - /projects/${user}/conda/pkgs

AEA developers may then create a local development environment with the following commands

.. code-block::

   $ source /apps/anaconda/3.12-anaconda-2024.10/etc/profile.d/conda.sh
   $ conda env create --name waves-env --file environment.yml
   $ conda activate waves-env

See the CI job Anaconda ``conda_installation`` path in ``.pipeline-common.yml`` for the current AEA Anaconda path and
version used by the AEA CI server.

HPC CI server environment
=========================

For computing policy reasons, HPC CI pipelines are owned by the launching user and launched with the user's account. The
HPC CI server environment is created in the user owned CI job directory, which is cleaned out for each CI job. This
means there is no shared environment available on HPC and developers must create and mantain their own development
environment. It is strongly recommended that developers create this environment in their scratch space, e.g.
``${system_scratch}/$USER/conda/envs/waves-env``.

Because the CI pipeline runs as the launching user, Conda will create a package and environment cache according to the
user's HPC Conda configuration. By default, Conda creates ``~/.conda/pkgs`` for the package cache, which can grow quite
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

HPC developers may then create a local development environment with the following commands

.. code-block::

   $ source /udsl/udsl1/hpcsoft/common/x86_64/anaconda/2024.10-python-3.12/etc/profile.d/conda.sh
   $ conda env create --name waves-env --file environment.yml
   $ conda activate waves

See the CI job Anaconda ``conda_installation`` path in ``.pipeline-hpc.yml`` for the current AEA Anaconda path and
version used by the AEA CI server.

Windows CI environment
======================

The Windows CI server must have a system (or Gitlab-Runner user) installation of the following software separately from
the Conda environment.

* Git
* Git-LFS
* TeXLive
* Anaconda/Miniconda/Miniforge

The Windows CI server environment is created under the default Gitlab-Runner user in the Gitlab-Runner build directory
and is not available for developers. The Windows CI jobs use a mix of the ``environment-win.yml``,
``conda-build.yml``, and ``pip-build.yml`` files. Windows developers may use ``environment-win.yml`` to create a local
development environment that closely mirrors the linux CI environment.

MacOS CI environment
====================

The MacOS CI server must have a system (or Gitlab-Runner user) installation of the following software separately from
the Conda environment.

* Git
* Git-LFS
* TeXLive
* Anaconda/Miniconda/Miniforge

The MacOS CI server environment is created under the default Gitlab-Runner user in the Gitlab-Runner build directory and
is not available for developers. The MacOS CI jobs use a mix of the ``environment.yml``, ``conda-build.yml``, and
``pip-build.yml`` files. MacOS developers may use the full ``environment.yml`` file to create a local development
environment that closely mirrors the linux CI environment.

.. include:: contribution.txt

.. _build:

*****
Build
*****

This project uses the `SCons`_ build system. This section will discuss some common build operations. For a full list of
`SCons`_ command-line options and target build behavior, see the `SCons manpage`_. The `SCons manpage`_ is also
installed with `Scons`_ in the environment and can be opened from the command-line as ``man scons`` in the `AEA Compute
environment`_.

- View project specific command-line options, default targets, and aliases

  .. code-block::

     $ scons -h

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

This project may be built as a Conda or pip package. The Conda package is the preferred distribution and takes the
default distribution name ``waves``. The Conda recipe(s) will call the pip build commands directly, so it is not
necessary to build the pip package first.

pip
===

To build the pip package, use the ``build`` alias. The package artifacts will live in ``build/dist``.

.. code-block::

   $ scons build

The package distribution name may be changed from the default ``waves`` to something else. For instance, on PyPI the
distribution name ``waves`` is taken by another project, so the PyPI distribution name of this project is
``waves-workflows``.

.. code-block::

   $ scons build --distribution-name=waves-workflows

For this reason the ``pyproject.toml`` file has been templated in the source tree as ``pyproject.toml.in``. The
necessary ``pyproject.toml`` file will be generated as necessary with the specified distribution name by the SCons
``build``, ``install``, ``style``, and test aliases.

The ``install`` alias is provided for packaging in ecosystems which support data file installation outside the package
directory, e.g. man pages. By default, this alias installs to a local ``install/`` directory, but the prefix may
be set to match the recipe's installation prefix. For instance, the Conda recipe must install to the ``${PREFIX}``
variable managed by ``conda-build``.

.. code-block::

   $ scons install --prefix=${PREFIX}

If a ``pyproject.toml`` file has been generated, the package may be built with the usual ``py-build`` and ``pip``
commands, as well. Such an installation will not include the man pages or HTML documentation and the ``waves docs``
subcommand will not work to launch locally installed documentation. Direct pip builds should be avoided as general
practice, but may be desirable for package maintainers that require more direct control over the build and install
options.

.. code-block::

   $ scons pyproject.toml
   $ python -m build .
   $ python -m pip install dist/waves-*.tar.gz

Conda
=====

To build the Conda package activate the development environment and run the conda build command found in the
CI configuration file. The current command may be found as

.. code-block::

   $ sed -n '/output_folder=/,/VERSION/p' .gitlab-ci.yml .pipeline*.yml
   ...

.. code-block::

   $ output_folder='conda-bld'
   $ mkdir ${output_folder}
   $ VERSION=$(python -m setuptools_scm) conda build recipe --channel conda-forge --no-anaconda-upload --output-folder ${output_folder}

A second recipe that bundles the LANL internally linked documentation is found in ``waves/recipe-internal`` and can be
built similarly by replacing ``recipe`` with ``recipe-internal`` in the above command.

Tutorials
=========

This project contains several, separate `SCons`_ project configurations, where the ``SConstruct`` file name indicates an
`SCons`_ project by convention. The |PROJECT| package and documentation are defined in the ``waves/SConstruct`` file.
The modsim template and regression tests are defined in a separate ``waves/modsim_template/Sconstruct`` file. The
|PROJECT| tutorials each have a tutorial specific configuration file ``waves/tutorials/*SConstruct``. The following
build commands apply to each, but must be run from their respective project configuration parent directories, ``waves``,
``waves/modsim_template`` and ``waves/tutorials``. The available targets and aliases differ accordingly.

When executing the tutorials or modsim template build commands directly in the repository, the |PROJECT| project root
repository must be put on ``PYTHONPATH``. In personal (*but not shared*) virtual environments, the preferred method is
to run ``conda develop .`` once from the project root directory. See the `Conda`_ documentation for more information
about "development" mode installs. For shared environments, the preferred solution is to prefix the build commands
with ``PYTHONPATH=.. ``, where it is assumed that the ``PWD`` is the tutorial or modsim template root directory.

.. code-block::

   $ pwd
   /home/roppenheimer/repos/waves/waves/modsim_template
   $ PYTHONPATH=/home/roppenheimer/repos/waves scons -h

****
Test
****

The project regression suite is collected under the ``regression`` alias and can be run as

.. code-block::

   $ scons regression

By default, the system tests are configured to run with permissive skips for missing third-party software. This allows
developers to run as much of the system test suite as possible on local systems with incomplete third-party software
installations. To force the full execution of the system tests, a pass-through ``--unconditional-build`` flag may be
added. This forces the documentation build, even if ``sphinx-build`` is missing, and passes through pytest to the system
tests and tutorials as an SCons CLI option of the same name. The AEA RHEL CI server contains all necessary third-party
software, so the CI tests on this server require the full build as

.. code-block::

   $ scons regression --unconditional-build

The continuous integration server also performs a separate style guide check using ``flake8`` and ``black`` with
associated aliases or the collector alias ``style``.

.. code-block::

   $ scons style

If ``black`` reports files that should be formatted, the following alias will format files using the same command line
options as the check alias. ``black`` can also be run directly, but this may miss files without the ``.py`` extension,
such as SConstruct and SConscript files. After formatting, the developer must review the changes and commit them to
their branch.

.. code-block::

   $ scons black-format

|PROJECT| has dedicated target aliases for the unit and system tests. To run the unit tests, activate a conda
environment and run

.. code-block::

   $ scons pytest

XML and HTML coverage reports are always generated for the ``pytest`` alias. The XML output is used to provide coverage
visualization on merge requests. The HTML output can be opened with a browser to explore coverage interactively and is
uploaded to the internally hosted Gitlab-Pages documentation at:
https://aea.re-pages.lanl.gov/python-projects/waves/coverage/index.html.

.. code-block::

   $ scons pytest
   $ ls build/pytest/coverage.xml build/pytest/coverage/index.html
   build/pytest/coverage.xml  build/pytest/coverage/index.html
   $ find build/pytest -name coverage.xml -o -name index.html
   build/pytest/coverage.xml
   build/pytest/coverage/index.html

.. warning::

   Since a v0.12.9 pre-release, the ``pyproject.toml`` file is templated from ``pyproject.toml.in`` to allow
   distribution name changes during packaging with ``scons build``. The SCons aliases which depend on ``pyproject.toml``
   will automatically create this templated file as necessary. However, if this file has not yet been generated, it is
   not possible to run the ``pytest`` executable directly. Run ``scons pyproject.toml`` or any of the testing aliases
   before running the test suite directly with the ``pytest`` command.

   .. code-block::

      $ scons pyproject.toml
      $ pytest -v -n 4 waves/_tests/test_scons_extensions.py

The tutorials and modsim template are run as system tests and require third-party software not available on conda-forge.
To run the system tests, install the third-party software and make them available in your ``PATH``, activate a conda
environment and run

.. code-block::

   $ scons systemtest

The full list of continuous integration test commands can be found in the Gitlab-CI files.

.. code-block::

   $ pwd
   path/to/local/git/clone/waves/
   $ sed -n '/developer-test/,/tags/p' .gitlab-ci.yml .pipeline-*.yml

The |PROJECT| unit and system tests may also be executed from the installation directory. These tests use pytest
directly and may require non-default pytest options and markers to execute the system tests serially. The full list of
CI commands may be found in the internal recipe file, ``recipe-internal/meta.yaml``, under the ``test`` keyword. The
following grep command will show the pytest commands and options.

.. code-block::

   $ grep "pytest " recipe-internal/*

Test Local Package
==================

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

- Build the `MODSIM-TEMPLATE`_ documentation. The |PROJECT| package must be on ``PYTHONPATH``. For developers, the least
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

*********
Gitlab-CI
*********

AEA RHEL
========

There are several known AEA RHEL CI fragile false-negative failure mechanisms. If one of these failures is observed,
try re-running the CI job without change.

* Conda environment creation fails in ``conda-build`` jobs. The shared conda command sometimes interferes with itself
  while running simultaneous ``conda-build`` jobs.

HPC
===

While the system tests are run with an HPC CI pipeline, the machine and runner uptime and system test runtime are
considered too fragile for reliable use. The AEA RHEL system tests pass in less than 8 minutes, but the HPC system
test job has been observed to complete in under 15 minutes or time out after an hour. The HPC CI system tests are
always run for merge-requests and scheduled pipelines, but the pass/fail status is not used to mark CI tests as
failing. Developers are encouraged to check the HPC system test results, but not required to address failing HPC CI
pipelines.

The HPC CI jobs usually run in 15-25 minutes when it runs successfully.

There are several known HPC CI fragile false-negative failure mechanisms. If one of these failures is observed, try
re-running the CI job without change.

* Timeout at 1 hour

Windows
=======

While the system tests are run with a Windows CI pipeline, the Windows CI server does not have the full suite of
third-party software required to run the full system tests. The pipeline is always run for merge-requests and
scheduled pipelines, but it is considered experimental and the pass/fail status is not used to mark CI tests as
failing. Developers are encouraged to check the Windows test results, but not required to address failing Windows CI
pipelines.

The Windows CI jobs usually run in under 6 minutes.

There are several known Windows CI fragile false-negative failure mechanisms. If one of these failures is observed,
try re-running the CI job without change.

* Incorrect or imcomplete CI environment build:
  ``Script file 'C:\ProgramData\anaconda3\envs\waves-dev\Scripts\sphinx-build-script.py' is not present.``

MacOS
=====

While the system tests are run with a MacOS CI pipeline, the MacOS CI server does not have the full suite of
third-party software required to run the full system tests. The pipeline is always run for merge-requests and
scheduled pipelines, but it is considered experimental and the pass/fail status is not used to mark CI tests as
failing. Developers are encouraged to check the MacOS test results, but not required to address failing MacOS CI
pipelines.

The MacOS CI jobs usually run in under 3 minutes.
