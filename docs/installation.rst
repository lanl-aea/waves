.. _installation:

############
Installation
############

.. only:: not aea

   *****
   Conda
   *****

   .. include:: README.txt
      :start-after: installation-conda-start-do-not-remove
      :end-before: installation-conda-end-do-not-remove

   ***
   pip
   ***

   .. include:: README.txt
      :start-after: installation-pip-start-do-not-remove
      :end-before: installation-pip-end-do-not-remove

   *****
   Spack
   *****

   .. include:: README.txt
      :start-after: installation-spack-start-do-not-remove
      :end-before: installation-spack-end-do-not-remove

.. only:: aea

   ***********
   Open source
   ***********

   Conda
   =====

   .. include:: README.txt
      :start-after: installation-conda-start-do-not-remove
      :end-before: installation-conda-end-do-not-remove

   pip
   ===

   .. include:: README.txt
      :start-after: installation-pip-start-do-not-remove
      :end-before: installation-pip-end-do-not-remove

   Spack
   =====

   .. include:: README.txt
      :start-after: installation-spack-start-do-not-remove
      :end-before: installation-spack-end-do-not-remove

   *************
   LANL internal
   *************

   |PROJECT| is released internally with continuous delivery practices. Production versions are released internally a
   month or two before the open-source release on conda-forge. The bleeding edge development version is released daily
   during active development cycles, often with several releases per day. Users can access the internal release through
   several mechanisms.

   For up-to-date AEA Conda channel instructions see the `AEA Conda channel`_ documentation.

   W-13/AEA RHEL servers
   =====================

   .. code-block::

      $ conda install --channel /projects/aea_compute/aea-conda waves

   HPC servers
   ===========

   .. code-block::

      $ conda install --channel /usr/projects/ea/aea_compute/aea-conda waves

   Gitlab package registry
   =======================

   Users with access to the |PROJECT| `upstream repository`_ or the `AEA Gitlab group`_ may also install from the
   experimental Gitlab PyPI-style package registry: https://re-git.lanl.gov/aea/python-projects/waves/-/packages.
   Click on a package to view in the Gitlab installation instructions, e.g.
   https://re-git.lanl.gov/aea/python-projects/waves/-/packages/19.
