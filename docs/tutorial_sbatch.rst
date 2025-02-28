.. _tutorial_sbatch:

##############################
Tutorial: Simulation via SLURM
##############################

.. include:: wip_warning.txt

This tutorial implements the same workflow introduced in :ref:`tutorial_simulation`, but executes the simulation
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

.. include:: tutorial_directory_setup.txt

.. note::

    If you skipped any of the previous tutorials, run the following commands to create a copy of the necessary tutorial
    files.

    .. code-block:: bash

        $ pwd
        /home/roppenheimer/waves-tutorials
        $ waves fetch --overwrite --tutorial 4 && mv tutorial_04_simulation_SConstruct SConstruct
        Destination directory: '/home/roppenheimer/waves-tutorials'

4. Download and copy the ``tutorial_04_simulation`` file to a new file named ``tutorial_sbatch``
   with the :ref:`waves_cli` :ref:`waves_fetch_cli` subcommand.

.. code-block:: bash

   $ pwd
   /home/roppenheimer/waves-tutorials
   $ waves fetch --overwrite tutorials/tutorial_04_simulation && cp tutorial_04_simulation tutorial_sbatch
   WAVES fetch
   Destination directory: '/home/roppenheimer/waves-tutorials'

.. _tutorials_tutorial_sbatch:

**********
SConscript
**********

A ``diff`` against the ``tutorial_04_simulation`` file from :ref:`tutorial_simulation` is included below to help identify the
changes made in this tutorial.

.. admonition:: waves-tutorials/tutorial_sbatch

   .. literalinclude:: tutorials_tutorial_sbatch
      :language: Python
      :diff: tutorials_tutorial_04_simulation

Note that the new ``AbaqusSolver`` builder will be conditionally defined in the ``SConstruct`` file according to the
availability of the ``sbatch`` command. If ``sbatch`` is not available, the ``slurm_job`` variable will go unused by the
:meth:`waves.scons_extensions.abaqus_solver_builder_factory`` builder. Since `SCons`_ builders don't throw errors for
unused keyword arguments, we do not need to define the task twice in the ``SConscript`` file.

**********
SConstruct
**********

A ``diff`` against the ``SConstruct`` file from :ref:`tutorial_simulation` is included below to help identify the
changes made in this tutorial.

.. admonition:: waves-tutorials/SConstruct

   .. literalinclude:: tutorials_tutorial_sbatch_SConstruct
      :language: Python
      :diff: tutorials_tutorial_04_simulation_SConstruct

*************
Build Targets
*************

5. Build the new targets

.. code-block:: bash

   $ pwd
   /home/roppenheimer/waves-tutorials
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
