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
features, start with :ref:`tutorialsconstruct`. It's also possible to skip the detailed project setup discussion and
start with the simulation task definitions and discussion directly in :ref:`tutorial_geometry_waves`.

Finally, users who are are ready to create their own modsim repository can use the :ref:`waves_cli`
:ref:`waves_quickstart_cli` subcommand to generate a modsim template directory structure from the single element example
model. The template files include project documentation and two simulation configurations: nominal and mesh convergence.

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
                   00:20 :ref:`tutorial_post_processing_waves`        Example solution to parameter study results
                                                                      concatenation with the parameter study definition
                   00:10 :ref:`tutorial_regression_testing_waves`     Alias for partial simulation verification and
                                                                      regression testing
                   00:10 :ref:`tutorial_archival_waves`               Archive simulation files for reproducibility and
                                                                      reporting
======================== ============================================ ==================================================

********************
Supplemental Lessons
********************

======================== ============================================ ==================================================
Time to complete (HH:MM) Tutorial                                     Summary
------------------------ -------------------------------------------- --------------------------------------------------
                   00:10 :ref:`scons_multiactiontask`                 Execute multiple actions on the same target file
                   00:20 :ref:`tutorial_cubit_waves`                  Geometry, partition, and mesh examples with Cubit
                                                                      replicating :ref:`tutorial_simulation_waves`
                   00:10 :ref:`tutorial_escape_sequences_waves`       Changing task actions without re-building the task
                   00:30 :ref:`tutorial_latin_hypercube_waves`        Parameter study introduction using a latin
                                                                      hypercube
                   00:30 :ref:`tutorial_sobol_sequence_waves`         Parameter study introduction using a Sobol
                                                                      sequence
                   00:30 :ref:`tutorial_mesh_convergence_waves`       Mesh convergence parameter study that uses
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
                   00:30 :ref:`tutorial_remote_execution_waves`       Run the simulation on a remote server via SSH
                   00:30 :ref:`tutorial_sbatch_waves`                 Run the simulation with the SLURM workload manager 
                   00:30 :ref:`tutorial_extend_study_waves`           Automatically extending and re-executing a
                                                                      parameter study
                   00:30 :ref:`tutorial_task_reuse_waves`             Re-use task definitions
                   00:10 :ref:`tutorial_setuptools_scm_waves`         Dynamic version number from git tags 
======================== ============================================ ==================================================
