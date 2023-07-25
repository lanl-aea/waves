.. target-start-do-not-remove

.. _Conda: https://docs.conda.io/en/latest/
.. _Conda installation: https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html
.. _Conda environment management: https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html
.. _SCons: https://scons.org/
.. _SCons documentation: https://scons.org/documentation.html
.. _SCons manpage: https://scons.org/doc/production/HTML/scons-man.html
.. _WAVES: https://lanl.github.io/waves/index.html
.. _WAVES repository: https://github.com/lanl/waves
.. _WAVES releases: https://github.com/lanl/waves/releases/
.. _WAVES-EABM: https://github.com/lanl/waves/tree/main/quickstart
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

.. image:: https://img.shields.io/github/actions/workflow/status/lanl/waves/pages.yml?branch=main&label=GitHub-Pages
   :target: https://lanl.github.io/waves/

.. image:: https://img.shields.io/github/v/release/lanl/waves?label=GitHub-Release
   :target: https://github.com/lanl/waves/releases

.. image:: https://img.shields.io/conda/vn/conda-forge/waves
   :target: https://anaconda.org/conda-forge/waves

.. image:: https://img.shields.io/conda/dn/conda-forge/waves.svg?label=Conda%20downloads
   :target: https://anaconda.org/conda-forge/waves

.. image:: https://zenodo.org/badge/591388602.svg
   :target: https://zenodo.org/badge/latestdoi/591388602

.. inclusion-marker-do-not-remove

***********
Description
***********

.. project-description-start-do-not-remove

`WAVES`_ (LANL code C23004) is a computational engineering workflow tool that integrates parametric studies with traditional software build systems.

In addition to the parametric study Python package and command line utilities, `WAVES`_ also includes `SCons`_ builders
for common engineering software used by model simulation (modsim) repositories. The tutorial simulations in this project
use `SCons`_ as the automated build system and translate software build system concepts in the language of engineering
simulation and analysis. The `SCons documentation`_ should be consulted as a reference for additional build system
concepts, command line options, and project configuration.

This project includes a template `WAVES-EABM`_ which is used for the tutorials and for integration and regression
testing of the `WAVES`_ extensions to SCons. The template modsim project can be duplicated from the command line as
``waves quickstart`` after installation.

.. project-description-end-do-not-remove

************
Installation
************

.. installation-start-do-not-remove

`WAVES`_ can be installed in a `Conda`_ environment with the `Conda`_ package manager. See the `Conda installation`_ and
`Conda environment management`_ documentation for more details about using `Conda`_.

.. code-block::

   $ conda install --channel conda-forge waves

.. installation-end-do-not-remove

*************
Documentation
*************

The documentation is bundled with the Conda package and can be accessed locally without a network connection after
installation from the command line as ``waves docs``. The documentation is also web-hosted:

* GitHub: https://lanl.github.io/waves/index.html
* LANL (``main`` branch): https://aea.re-pages.lanl.gov/python-projects/waves/main/
* LANL (``dev`` branch): https://aea.re-pages.lanl.gov/python-projects/waves/dev/

The `WAVES-EABM documentation`_ is hosted as a separate webpage as a demonstration for what EABM documentation can look
like.

* GitHub (pending): https://lanl.github.io/waves/waves-eabm/index.html
* LANL (``main`` branch): https://aea.re-pages.lanl.gov/python-projects/waves/main/waves-eabm/
* LANL (``dev`` branch): https://aea.re-pages.lanl.gov/python-projects/waves/dev/waves-eabm/

**********
Developers
**********

* `Kyle Brindley`_
* `Prabhu Khalsa`_
* `Thomas Roberts`_
* `Sergio Cordova`_
* `Matthew Fister`_
* `Scott Ouellette`_

****************
Copyright Notice
****************

.. copyright-start-do-not-remove

Copyright (c) 2023, Triad National Security, LLC. All rights reserved.

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

* GitHub: https://lanl.github.io/waves/devops.html
* LANL: https://aea.re-pages.lanl.gov/python-projects/waves/dev/devops.html

Clone the project
=================

.. clone-start-do-not-remove

* GitHub

  .. code-block::

     $ git clone git@github.com:lanl/waves.git

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

.. env-end-do-not-remove

Documentation
=============

.. docs-start-do-not-remove

The documentation build is automated with SCons as the ``documentation`` target.

- Build the `WAVES`_ documentation

  .. code-block::

     $ pwd
     path/to/local/git/clone/waves/
     $ scons documentation

.. docs-end-do-not-remove

