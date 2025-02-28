.. _tutorial_escape_sequences:

##########################
Tutorial: Escape Sequences
##########################

In addition to source and target file signatures, SCons saves a build signature that includes information about the
action required to build the target. The build signature will include the substitution variables used in the task. For
example, the contents of the ``abaqus_options`` string provided to the
:meth:`waves.scons_extensions.abaqus_journal_builder_factory` and
:meth:`waves.scons_extensions.abaqus_solver_builder_factory` builders is part of the build signature. Changes to these
options will trigger a re-build of that task.

Sometimes you may want to exclude elements of the task action from the build signature. For instance, the Solve step
introduced in :ref:`tutorial_simulation` can run Abaqus with a different number of cpus, which shouldn't affect
the simulation results. Adding a variable number of cpus to the ``abaqus_options`` would change the build signature each
time the cpu count changed and unnecessarily re-run the simulation task. To avoid this, you can specify elements of the
action to exclude from the build signature with the ``$( excluded string $)`` escape sequence syntax.

**********
References
**********

* `SCons Variable Substitution`_ :cite:`scons-man`

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

4. Download and copy the ``tutorial_04_simulation`` file to a new file named ``tutorial_escape_sequences``
   with the :ref:`waves_cli` :ref:`waves_fetch_cli` subcommand.

.. code-block:: bash

   $ pwd
   /home/roppenheimer/waves-tutorials
   $ waves fetch --overwrite tutorials/tutorial_04_simulation && cp tutorial_04_simulation tutorial_escape_sequences
   WAVES fetch
   Destination directory: '/home/roppenheimer/waves-tutorials'

.. _tutorials_tutorial_escape_sequences:

**********
SConscript
**********

A ``diff`` against the ``tutorial_04_simulation`` file from :ref:`tutorial_simulation` is included below to help identify the
changes made in this tutorial.

.. admonition:: waves-tutorials/tutorial_escape_sequences

   .. literalinclude:: tutorials_tutorial_escape_sequences
      :language: Python
      :diff: tutorials_tutorial_04_simulation

**********
SConstruct
**********

A ``diff`` against the ``SConstruct`` file from :ref:`tutorial_simulation` is included below to help identify the
changes made in this tutorial.

.. admonition:: waves-tutorials/SConstruct

   .. literalinclude:: tutorials_tutorial_escape_sequences_SConstruct
      :language: Python
      :diff: tutorials_tutorial_04_simulation_SConstruct

*************
Build Targets
*************

5. Build the new targets

.. code-block:: bash

   $ pwd
   /home/roppenheimer/waves-tutorials
   $ scons tutorial_escape_sequences
   scons: Reading SConscript files ...
   Checking whether abq2024 program exists.../apps/abaqus/Commands/abq2024
   Checking whether abq2021 program exists.../apps/abaqus/Commands/abq2021
   Checking whether abq2020 program exists.../apps/abaqus/Commands/abq2020
   scons: done reading SConscript files.
   scons: Building targets ...
   cd /home/roppenheimer/waves-tutorials/build/tutorial_escape_sequences && /apps/abaqus/Commands/abq2024 cae -noGui /home/roppenheimer/waves-tutorials/modsim_package/abaqus/rectangle_geometry.py -- > rectangle_geometry.stdout 2>&1
   cd /home/roppenheimer/waves-tutorials/build/tutorial_escape_sequences && /apps/abaqus/Commands/abq2024 cae -noGui /home/roppenheimer/waves-tutorials/modsim_package/abaqus/rectangle_partition.py -- > rectangle_partition.stdout 2>&1
   cd /home/roppenheimer/waves-tutorials/build/tutorial_escape_sequences && /apps/abaqus/Commands/abq2024 cae -noGui /home/roppenheimer/waves-tutorials/modsim_package/abaqus/rectangle_mesh.py -- > rectangle_mesh.stdout 2>&1
   Copy("build/tutorial_escape_sequences/rectangle_compression.inp", "modsim_package/abaqus/rectangle_compression.inp")
   Copy("build/tutorial_escape_sequences/assembly.inp", "modsim_package/abaqus/assembly.inp")
   Copy("build/tutorial_escape_sequences/boundary.inp", "modsim_package/abaqus/boundary.inp")
   Copy("build/tutorial_escape_sequences/field_output.inp", "modsim_package/abaqus/field_output.inp")
   Copy("build/tutorial_escape_sequences/materials.inp", "modsim_package/abaqus/materials.inp")
   Copy("build/tutorial_escape_sequences/parts.inp", "modsim_package/abaqus/parts.inp")
   Copy("build/tutorial_escape_sequences/history_output.inp", "modsim_package/abaqus/history_output.inp")
   cd /home/roppenheimer/waves-tutorials/build/tutorial_escape_sequences && /apps/abaqus/Commands/abq2024 -job rectangle_compression -input rectangle_compression -double both -cpus 1 -interactive -ask_delete no > rectangle_compression.stdout 2>&1
   scons: done building targets.

6. Execute the build command again with a different number of solve cpus. Observe that the workflow is reported as
   up-to-date.

.. code-block::

   $ pwd
   /path/to/waves-tutorials
   $ scons tutorial_escape_sequences --solve-cpus=2
   scons: Reading SConscript files ...
   Checking whether abq2021 program exists.../apps/abaqus/Commands/abq2021
   Checking whether abq2020 program exists.../apps/abaqus/Commands/abq2020
   scons: done reading SConscript files.
   scons: Building targets ...
   scons: `tutorial_escape_sequences' is up to date.
   scons: done building targets.

************
Output Files
************

Explore the contents of the ``build`` directory using the ``tree`` command against the ``build`` directory, as shown
below. Note that the output files from the previous tutorials also exist in the ``build`` directory, but the directory
is specified by name to reduce clutter in the ouptut shown.

.. code-block:: bash

   $ pwd
   /home/roppenheimer/waves-tutorials
   $ tree build/tutorial_escape_sequences/
   build/tutorial_escape_sequences/
   |-- abaqus.rpy
   |-- abaqus.rpy.1
   |-- abaqus.rpy.2
   |-- assembly.inp
   |-- boundary.inp
   |-- field_output.inp
   |-- history_output.inp
   |-- materials.inp
   |-- parts.inp
   |-- rectangle_compression.com
   |-- rectangle_compression.dat
   |-- rectangle_compression.inp
   |-- rectangle_compression.msg
   |-- rectangle_compression.odb
   |-- rectangle_compression.prt
   |-- rectangle_compression.sta
   |-- rectangle_compression.stdout
   |-- rectangle_geometry.cae
   |-- rectangle_geometry.jnl
   |-- rectangle_geometry.stdout
   |-- rectangle_mesh.cae
   |-- rectangle_mesh.inp
   |-- rectangle_mesh.jnl
   |-- rectangle_mesh.stdout
   |-- rectangle_partition.cae
   |-- rectangle_partition.jnl
   `-- rectangle_partition.stdout

   0 directories, 27 files
