.. _tutorial_introduction:

#####################
Tutorial Introduction
#####################

*************
Start Options
*************

Users who want to jump straight to a minimally functional simulation workflow with native `SCons`_ can start with the
:ref:`scons_quickstart`. The :ref:`waves_quickstart` has the same features but uses the `WAVES`_ extension to `SCons`_.
For a detailed discussion of a recommended best practices `SCons`_  and `WAVES-EABM`_ project setup, meta data, and
features, start with :ref:`tutorialsconstruct`. It's also possible to skip the detailed project setup discussion and
start with the simulation task definitions and discussion directly in :ref:`tutorial_geometry_waves`.

*************
Prerequisites
*************

.. include:: tutorial_00_prerequisites.txt

********
Schedule
********

Quickstart
==========

======================== ============================================ ==================================================
Time to complete (HH:MM) Tutorial                                     Summary
------------------------ -------------------------------------------- --------------------------------------------------
                   00:10 :ref:`scons_quickstart`                      Minimally functional simulation build system
                                                                      workflow using pure `SCons`_
                   00:10 :ref:`waves_quickstart`                      Minimally functional simulation build system
                                                                      workflow using `SCons`_ and `WAVES`_
======================== ============================================ ==================================================

Core Lessons
============

======================== ============================================ ==================================================
Time to complete (HH:MM) Tutorial                                     Summary
------------------------ -------------------------------------------- --------------------------------------------------
                   01:00 :ref:`tutorialsconstruct`                    `SCons`_ project definition and meta data
                   01:00 :ref:`tutorial_geometry_waves`               Hierarchical `SCons`_ builds, task creation,
                                                                      Abaqus journal files as small utility software
                   00:45 :ref:`tutorial_partition_mesh_waves`         Dependent tasks and execution order
                   00:20 :ref:`tutorial_solverprep_waves`             Copying files into the build directory
                   00:20 :ref:`tutorial_simulation_waves`             Abaqus solver execution
                   00:20 :ref:`tutorial_parameter_substitution_waves` Parameterized builds and substituting parameter
                                                                      values into copied files
                   00:20 :ref:`tutorial_include_files_waves`          Including files that can be re-used in more than
                                                                      one workflow
                   00:30 :ref:`tutorial_cartesian_product_waves`      Parameter study introduction using a cartesian
                                                                      product
                   00:20 :ref:`tutorial_data_extraction_waves`        Abaqus data extraction
======================== ============================================ ==================================================

Supplemental Lessons
====================

======================== ============================================ ==================================================
Time to complete (HH:MM) Tutorial                                     Summary
------------------------ -------------------------------------------- --------------------------------------------------
                   00:20 :ref:`tutorial_cubit_waves`                  Geometry, partition, and mesh examples with Cubit
                                                                      replicating :ref:`tutorial_simulation_waves`
                   00:10 :ref:`scons_multiactiontask`                 Execute multiple actions on the same target file
                   00:30 :ref:`tutorial_cartesian_product_waves`      Parameter study introduction using a latin
                                                                      hypercube
======================== ============================================ ==================================================
