.. _tutorial_introduction:

#####################
Tutorial Introduction
#####################

*************
Start Options
*************

Users who want to jump straight to a minimally functional simulation workflow with native `SCons`_ can start with the
:ref:`scons_quickstart`. The :ref:`waves_quickstart` has the same features but uses the `WAVES`_ extension to `SCons`_.

For a detailed discussion of recommended best practices for `SCons`_  and `WAVES-EABM`_ project setup, meta data, and
features, start with :ref:`tutorialsconstruct`. Most of the ``SContruct`` file introduced in :ref:`tutorialsconstruct`
is boilerplate code, so users may want to skip straight to the workflow task definitions in
:ref:`tutorial_geometry`. An optional ``waves fetch`` command is included in :ref:`tutorial_geometry` to
help users create the content of :ref:`tutorialsconstruct`. The :ref:`waves_cli` :ref:`waves_fetch_cli` subcommand may
also be used to create a local copy of any tutorial file.

.. include:: modsim_templates.txt

*************
Prerequisites
*************

.. include:: tutorial_00_prerequisites.txt

**********
Quickstart
**********

======================== ============================================ ==================================================
Time to complete (HH:MM) Tutorial                                     Summary
------------------------ -------------------------------------------- --------------------------------------------------
                   00:10 :ref:`scons_quickstart`                      Minimally functional simulation build system
                                                                      workflow using pure `SCons`_
                   00:10 :ref:`waves_quickstart`                      Minimally functional simulation build system
                                                                      workflow using `SCons`_ and `WAVES`_
======================== ============================================ ==================================================

************
Core Lessons
************

======================== ============================================ ==================================================
Time to complete (HH:MM) Tutorial                                     Summary
------------------------ -------------------------------------------- --------------------------------------------------
                   01:00 :ref:`tutorialsconstruct`                    `SCons`_ project configuration and meta data
                   01:00 :ref:`tutorial_geometry`                     Hierarchical `SCons`_ builds, task creation,
                                                                      Abaqus journal files as small utility software
                   00:45 :ref:`tutorial_partition_mesh`               Dependent tasks and execution order
                   00:20 :ref:`tutorial_solverprep`                   Copying files into the build directory
                   00:20 :ref:`tutorial_simulation`                   Abaqus solver execution
                   00:20 :ref:`tutorial_parameter_substitution`       Parameterized builds and substituting parameter
                                                                      values into copied files
                   00:20 :ref:`tutorial_include_files`                Including files that can be re-used in more than
                                                                      one workflow
                   00:30 :ref:`tutorial_cartesian_product`            Parameter study introduction using a cartesian
                                                                      product
                   00:20 :ref:`tutorial_data_extraction`              Abaqus data extraction
                   00:30 :ref:`tutorial_post_processing`              Example solution to parameter study results
                                                                      concatenation with the parameter study definition
                   00:20 :ref:`tutorial_unit_testing`                 Unit testing
                   00:10 :ref:`tutorial_regression_testing`           Alias for partial simulation verification and
                                                                      regression testing
                   00:10 :ref:`tutorial_archival`                     Archive simulation files for reproducibility and
                                                                      reporting
======================== ============================================ ==================================================

********************
Supplemental Lessons
********************

======================== ============================================ ==================================================
Time to complete (HH:MM) Tutorial                                     Summary
------------------------ -------------------------------------------- --------------------------------------------------
                   00:10 :ref:`scons_multiactiontask`                 Execute multiple actions on the same target file
                   00:20 :ref:`tutorial_argparse_types`               Add input verification to workflow parameters
                   00:20 :ref:`tutorial_cubit_abaqus`                 Geometry, partition, and mesh examples with Cubit
                                                                      replicating :ref:`tutorial_simulation`
                   00:20 :ref:`tutorial_cubit_sierra`                 Side-by-side Abaqus and Sierra workflows
                                                                      complementing :ref:`tutorial_cubit_abaqus`
                   00:10 :ref:`tutorial_escape_sequences`             Changing task actions without re-building the task
                   00:30 :ref:`tutorial_latin_hypercube`              Parameter study introduction using a latin
                                                                      hypercube
                   00:30 :ref:`tutorial_sobol_sequence`               Parameter study introduction using a Sobol
                                                                      sequence
                   00:30 :ref:`tutorial_mesh_convergence`             Mesh convergence parameter study that uses
                                                                      common Geometry and Partition tasks.
======================== ============================================ ==================================================

************************
Work-in-progress Lessons
************************

.. warning::

   The lessons in this section represent `WAVES`_ features in the "alpha" development stage or draft solutions to common
   problems that require additional user testing to better define the user story, needs, and desired behavior.

======================== ============================================ ==================================================
Time to complete (HH:MM) Tutorial                                     Summary
------------------------ -------------------------------------------- --------------------------------------------------
                   00:30 :ref:`tutorial_remote_execution`             Run the simulation on a remote server via SSH
                   00:30 :ref:`tutorial_sbatch`                       Run the simulation with the SLURM workload manager
                   00:30 :ref:`tutorial_extend_study`                 Automatically extending and re-executing a
                                                                      parameter study
                   00:30 :ref:`tutorial_task_reuse`                   Re-use task definitions
                   00:10 :ref:`tutorial_setuptools_scm`               Dynamic version number from git tags
======================== ============================================ ==================================================
