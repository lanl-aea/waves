.. target-start-do-not-remove

.. _Conda: https://docs.conda.io/en/latest/
.. _Conda installation: https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html
.. _Conda environment management: https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html
.. _PyPI: https://pypi.org/
.. _pip: https://pip.pypa.io/en/stable/
.. _SCons: https://scons.org/
.. _SCons documentation: https://scons.org/documentation.html
.. _SCons manpage: https://scons.org/doc/production/HTML/scons-man.html
.. _Spack: https://spack.io/
.. _WAVES: https://lanl-aea.github.io/waves/index.html
.. _WAVES repository: https://github.com/lanl-aea/waves
.. _WAVES releases: https://github.com/lanl-aea/waves/releases/
.. _MODSIM-TEMPLATE: https://github.com/lanl-aea/waves/tree/main/waves/modsim_template
.. _MODSIM-TEMPLATE documentation: https://lanl-aea.github.io/waves/modsim-template/index.html

.. _`Kyle Brindley`: kbrindley@lanl.gov
.. _`Thomas Roberts`: tproberts@lanl.gov
.. _`Sergio Cordova`: sergioc@lanl.gov
.. _`Prabhu Khalsa`: pkhalsa@lanl.gov
.. _`Scott Ouellette`: souellette@lanl.gov
.. _`Chris Johnson`: clj@lanl.gov
.. _`Matthew Fister`: mwfister@lanl.gov

.. target-end-do-not-remove

#####
WAVES
#####

.. image:: https://img.shields.io/github/actions/workflow/status/lanl-aea/waves/pages.yml?branch=main&label=GitHub-Pages
   :target: https://lanl-aea.github.io/waves/

.. image:: https://img.shields.io/github/v/release/lanl-aea/waves?label=GitHub-Release
   :target: https://github.com/lanl-aea/waves/releases

.. image:: https://img.shields.io/conda/vn/conda-forge/waves
   :target: https://anaconda.org/conda-forge/waves

.. image:: https://img.shields.io/conda/dn/conda-forge/waves.svg?label=Conda%20downloads
   :target: https://anaconda.org/conda-forge/waves

.. image:: https://img.shields.io/pypi/v/waves-workflows?label=PyPI%20package
   :target: https://pypi.org/project/waves-workflows/

.. image:: https://img.shields.io/pypi/dm/waves-workflows?label=PyPI%20downloads
   :target: https://pypi.org/project/waves-workflows/

.. image:: https://zenodo.org/badge/591388602.svg
   :target: https://zenodo.org/badge/latestdoi/591388602

.. inclusion-marker-do-not-remove

***********
Description
***********

.. project-description-start-do-not-remove

`WAVES`_ (LANL code C23004) is a computational science and engineering workflow tool that integrates parametric studies
with traditional software build systems.

In addition to the parametric study Python package and command line utilities, `WAVES`_ also includes `SCons`_ builders
for common engineering software used by model simulation (modsim) repositories. The tutorial simulations in this project
use `SCons`_ as the automated build system and translate software build system concepts in the language of engineering
simulation and analysis. The `SCons documentation`_ should be consulted as a reference for additional build system
concepts, command line options, and project configuration.

This project includes a `MODSIM-TEMPLATE`_ which is used for the tutorials and for integration and regression testing of
the `WAVES`_ extensions to SCons. The template modsim project can be duplicated from the command line as ``waves fetch
modsim_template`` after installation.

.. project-description-end-do-not-remove

************
Installation
************

Conda
=====

.. installation-conda-start-do-not-remove

`WAVES`_ can be installed in a `Conda`_ environment with the `Conda`_ package manager. See the `Conda installation`_ and
`Conda environment management`_ documentation for more details about using `Conda`_.

.. code-block::

   $ conda install --channel conda-forge waves

.. installation-conda-end-do-not-remove

pip
===

.. installation-pip-start-do-not-remove

`WAVES`_ may also be installed from `PyPI`_ with `pip`_ under the distribution name ``waves-workflows``:
https://pypi.org/project/waves-workflows/. The package installs and imports as ``waves``, so care must be taken to avoid
name clashes with similarly named `PyPI`_ packages.

.. code-block::

   $ pip install waves-workflows

.. installation-pip-end-do-not-remove

Spack
=====

.. installation-spack-start-do-not-remove

`WAVES`_ may be installed with the `Spack`_ package manager under the distribution name ``py-waves``:
https://packages.spack.io/package.html?name=py-waves. The package installs and imports as ``waves``.

.. code-block::

   $ spack install py-waves

.. installation-spack-end-do-not-remove

*************
Documentation
*************

The documentation is bundled with the Conda package and can be accessed locally without a network connection after
installation from the command line as ``waves docs``. The documentation is also web-hosted:

* GitHub: https://lanl-aea.github.io/waves/index.html
* LANL: https://aea.re-pages.lanl.gov/python-projects/waves/

The `MODSIM-TEMPLATE documentation`_ is hosted as a separate webpage as a demonstration for what modsim project
documentation can look like.

* GitHub: https://lanl-aea.github.io/waves/modsim-template/index.html
* LANL: https://aea.re-pages.lanl.gov/python-projects/waves/modsim-template/

**********
Developers
**********

* `Kyle Brindley`_
* `Prabhu Khalsa`_
* `Thomas Roberts`_
* `Sergio Cordova`_
* `Matthew Fister`_
* `Chris Johnson`_
* `Scott Ouellette`_

****************
Copyright Notice
****************

.. copyright-start-do-not-remove

Copyright (c) 2022-2025, Triad National Security, LLC. All rights reserved.

This program was produced under U.S. Government contract 89233218CNA000001 for Los Alamos National Laboratory (LANL),
which is operated by Triad National Security, LLC for the U.S.  Department of Energy/National Nuclear Security
Administration. All rights in the program are reserved by Triad National Security, LLC, and the U.S. Department of
Energy/National Nuclear Security Administration. The Government is granted for itself and others acting on its behalf a
nonexclusive, paid-up, irrevocable worldwide license in this material to reproduce, prepare derivative works, distribute
copies to the public, perform publicly and display publicly, and to permit others to do so.

.. copyright-end-do-not-remove

***************
Developer Notes
***************

The full developer manual can be found at:

* GitHub: https://lanl-aea.github.io/waves/devops.html
* LANL: https://aea.re-pages.lanl.gov/python-projects/waves/devops.html

Clone the project
=================

.. clone-start-do-not-remove

* GitHub

  .. code-block::

     $ git clone git@github.com:lanl-aea/waves.git

* LANL

  .. code-block::

     $ git clone ssh://git@re-git.lanl.gov:10022/aea/python-projects/waves.git

.. clone-end-do-not-remove

Local development environments
==============================

.. env-start-do-not-remove

`SCons`_ can be installed in a `Conda`_ environment with the `Conda`_ package manager. See the `Conda installation`_ and
`Conda environment management`_ documentation for more details about using `Conda`_.

1. Create the environment if it doesn't exist

   .. code-block::

      $ pwd
      path/to/local/git/clone/waves
      $ conda env create --name waves-env --file environment.yml

2. Activate the environment

   .. code-block::

      $ conda activate waves-env

In addition to the primary development environment file ``environment.yml``, several other environment files are
maintained for CI jobs. For Windows developers, ``environment-win.yml`` removes packages that are not available for
Windows and packages that are only necessary for deployment jobs. The ``conda-build.yml`` and ``pip-build.yml`` are
stripped down to the bare essentials for building `Conda`_ and `pip`_ packages, respectively.

.. env-end-do-not-remove

Documentation
=============

.. docs-start-do-not-remove

The documentation build is automated with SCons as the ``documentation`` target. The HTML documentation builds to
``waves/build/docs/html/index.html``

- Build the `WAVES`_ documentation

  .. code-block::

     $ pwd
     path/to/local/git/clone/waves/
     $ scons documentation

.. docs-end-do-not-remove

