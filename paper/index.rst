###################################
Engineering Computational Practices
###################################

.. note::

   This paper describes the core concepts for the `WAVES`_ software :cite:`WAVES`. The software is undergoing the Los
   Alamos National Laboratory licensing and release process. This paper will be followed by the full documentation
   :cite:`WAVES` of `WAVES`_ pending the open source release.

   Until the open source release of `WAVES`_, the :ref:`user_manual` introduces the build system concepts implemented
   directly in `SCons`_. These tutorials lack the parametric study tools, but can be implemented with currently
   available open-source packages.

.. include:: project_brief.txt

.. raw:: latex

   \part{Computational Practices}

.. _computational_tools:

.. toctree::
   :maxdepth: 1
   :caption: Computational Practices

   computational_practices_introduction
   computational_practices_version_control
   computational_practices_documentation
   computational_practices_build_system
   computational_practices_compute_environment
   computational_practices_regression_testing

.. raw:: latex

   \part{User Manual}

.. _user_manual:

.. toctree::
   :maxdepth: 1
   :caption: User Manual

   scons_quickstart
   scons_multiactiontask

.. raw:: latex

   \part{Appendices}

.. toctree::
   :caption: Appendices
   :maxdepth: 1

   eabm_api
   eabm_cli
   eabm_abaqus_files
   glossary
   zreferences
