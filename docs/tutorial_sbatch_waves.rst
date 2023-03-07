.. _tutorial_sbatch_waves:

##############################
Tutorial: Simulation via SLURM
##############################

.. include:: wip_warning.txt

This tutorial implements the same workflow introduced in :ref:`tutorial_simulation_waves`, but executes the simulation
with the SLURM workload manager.

**********
References
**********

* `SLURM`_ `sbatch`_ :cite:`slurm`

***********
Environment
***********

.. include:: tutorial_environment_activation.txt

*******************
Directory Structure
*******************

3. Copy the ``tutorial_04_simulation`` file to a new file named ``tutorial_sbatch``

.. code-block:: bash

   $ pwd
   /path/to/waves-tutorials
   $ cp tutorial_04_simulation tutorial_sbatch

.. _tutorials_tutorial_sbatch_waves:

**********
SConscript
**********

A ``diff`` against the ``tutorial_04_simulation`` file from :ref:`tutorial_simulation_waves` is included below to help identify the
changes made in this tutorial.

.. admonition:: waves-tutorials/tutorial_sbatch

   .. literalinclude:: tutorials_tutorial_sbatch
      :language: Python
      :diff: tutorials_tutorial_04_simulation

Note that the new ``AbaqusSolver`` builder will be conditionally defined in the ``SConstruct`` file according to the
availability of the ``sbatch`` command. If ``sbatch`` is not available, the ``slurm_job`` variable will go unused by the
:meth:`waves.builders.abaqus_solver`` builder. Since `SCons`_ builders don't throw errors for unused keyword arguments,
we do not need to define the task twice in the ``SConscript`` file.

**********
SConstruct
**********

A ``diff`` against the ``SConstruct`` file from :ref:`tutorial_simulation_waves` is included below to help identify the
changes made in this tutorial.

.. admonition:: waves-tutorials/SConstruct

   .. literalinclude:: tutorials_tutorial_sbatch_SConstruct
      :language: Python
      :diff: tutorials_tutorial_04_simulation_SConstruct

*************
Build Targets
*************

4. Build the new targets

.. code-block:: bash

   $ pwd
   /path/to/waves-tutorials
   $ scons tutorial_sbatch

************
Output Files
************

Explore the contents of the ``build`` directory using the ``tree`` command against the ``build`` directory, as shown
below. Note that the output files from the previous tutorials also exist in the ``build`` directory, but the directory
is specified by name to reduce clutter in the ouptut shown.

.. code-block:: bash

   $ pwd
   /home/roppenheimer/waves-tutorials
   $ tree build/tutorial_sbatch/
