.. _tutorial_escape_sequences_waves:

##########################
Tutorial: Escape Sequences
##########################

In addition to source and target file signatures, SCons saves a build signature that includes information about the
action required to build the target. The build signature will include the substitution variables used in the task. For
example, the contents of the ``abaqus_options`` string provided to the :meth:`waves.builders.abaqus_journal` and
:meth:`waves.builders.abaqus_solver` builders is part of the build signature. Changes to these options will trigger a
re-build of that task.

Sometimes you may want to exclude elements of the task action from the build signature. For instance, the Solve step
introduced in :ref:`tutorial_simulation_waves` can run Abaqus with a different number of cpus, which shouldn't affect
the simulation results. Adding a variable number of cpus to the ``abaqus_options`` would change the build signature each
time the cpu count changed and unnecessarily re-run the simulation task. To avoid this, you can specify elements of the
action to exclude from the build signature with the ``$( excluded string $)`` escape sequence syntax.

**********
References
**********

* `SCons`_ Variable Substitution :cite:`scons-man`

The relevant portion of the `SCons`_ documentation can't be hyperlinked directly. Instead, the relevant portion of the
"Substitution Variables" section of the man pages is quoted below :cite:`scons-man`.

   When a build action is executed, a hash of the command line is saved, together with other information about the
   target(s) built by the action, for future use in rebuild determination. This is called the *build signature* (or *build
   action signature*). The escape sequence **$(** *subexpression* **$)** may be used to indicate parts of a command line that may
   change without causing a rebuild--that is, which are not to be included when calculating the build signature. All text
   from **$(** up to and including the matching **$)** will be removed from the command line before it is added to the build
   signature while only the **$(** and **$)** will be removed before the command is executed. For example, the command line string:

   .. code-block:: bash

      "echo Last build occurred $( $TODAY $). > $TARGET"

   would execute the command:

   .. code-block:: bash

      echo Last build occurred $TODAY. > $TARGET

   but the build signature added to any target files would be computed from:

   .. code-block:: bash

      echo Last build occurred  . > $TARGET

***********
Environment
***********

.. include:: tutorial_environment_activation.txt

*******************
Directory Structure
*******************

3. Create a directory ``tutorial_escape_sequences`` in the ``waves-eabm-tutorial`` directory.

.. code-block:: bash

   $ pwd
   /path/to/waves-eabm-tutorial
   $ mkdir -p tutorial_escape_sequences eabm_package_cubit

4. Copy the ``tutorial_04_simulation/SConscript`` file into the newly created ``tutorial_escape_sequences``
   directory.

.. code-block:: bash

   $ pwd
   /path/to/waves-eabm-tutorial
   $ cp tutorial_04_simulation/SConscript tutorial_escape_sequences/

.. _tutorial_escape_sequences_waves_SConscript:

**********
SConscript
**********

A ``diff`` against the ``SConscript`` file from :ref:`tutorial_simulation_waves` is included below to help identify the
changes made in this tutorial.

.. admonition:: waves-eabm-tutorial/tutorial_escape_sequences/SConscript

   .. literalinclude:: tutorial_escape_sequences_SConscript
      :language: Python
      :diff: tutorial_04_simulation_SConscript

**********
SConstruct
**********

A ``diff`` against the ``SConstruct`` file from :ref:`tutorial_simulation_waves` is included below to help identify the
changes made in this tutorial.

.. admonition:: waves-eabm-tutorial/SConstruct

   .. literalinclude:: eabm_tutorial_escape_sequences_SConstruct
      :language: Python
      :diff: eabm_tutorial_04_simulation_SConstruct

*************
Build Targets
*************

6. Build the new targets

.. code-block:: bash

   $ pwd
   /path/to/waves-eabm-tutorial
   $ scons tutorial_escape_sequences
   scons: Reading SConscript files ...
   Checking whether abq2021 program exists.../apps/abaqus/Commands/abq2021
   Checking whether abq2020 program exists.../apps/abaqus/Commands/abq2020
   scons: done reading SConscript files.
   scons: Building targets ...
   cd /home/roppenheimer/waves-eabm-tutorial/build/tutorial_escape_sequences && /apps/abaqus/Commands/abq2021 -information environment > single_element_geometry.abaqus_v6.env
   cd /home/roppenheimer/waves-eabm-tutorial/build/tutorial_escape_sequences && /apps/abaqus/Commands/abq2021 cae -noGui /home/roppenheimer/waves-eabm-tutorial/eabm_package/abaqus/single_element_geometry.py -- > single_element_geometry.stdout 2>&1
   cd /home/roppenheimer/waves-eabm-tutorial/build/tutorial_escape_sequences && /apps/abaqus/Commands/abq2021 -information environment > single_element_partition.abaqus_v6.env
   cd /home/roppenheimer/waves-eabm-tutorial/build/tutorial_escape_sequences && /apps/abaqus/Commands/abq2021 cae -noGui /home/roppenheimer/waves-eabm-tutorial/eabm_package/abaqus/single_element_partition.py -- > single_element_partition.stdout 2>&1
   cd /home/roppenheimer/waves-eabm-tutorial/build/tutorial_escape_sequences && /apps/abaqus/Commands/abq2021 -information environment > single_element_mesh.abaqus_v6.env
   cd /home/roppenheimer/waves-eabm-tutorial/build/tutorial_escape_sequences && /apps/abaqus/Commands/abq2021 cae -noGui /home/roppenheimer/waves-eabm-tutorial/eabm_package/abaqus/single_element_mesh.py -- > single_element_mesh.stdout 2>&1
   Copy("build/tutorial_escape_sequences/single_element_compression.inp", "eabm_package/abaqus/single_element_compression.inp")
   Copy("build/tutorial_escape_sequences/assembly.inp", "eabm_package/abaqus/assembly.inp")
   Copy("build/tutorial_escape_sequences/boundary.inp", "eabm_package/abaqus/boundary.inp")
   Copy("build/tutorial_escape_sequences/field_output.inp", "eabm_package/abaqus/field_output.inp")
   Copy("build/tutorial_escape_sequences/materials.inp", "eabm_package/abaqus/materials.inp")
   Copy("build/tutorial_escape_sequences/parts.inp", "eabm_package/abaqus/parts.inp")
   Copy("build/tutorial_escape_sequences/history_output.inp", "eabm_package/abaqus/history_output.inp")
   cd /home/roppenheimer/waves-eabm-tutorial/build/tutorial_escape_sequences && /apps/abaqus/Commands/abq2021 -information environment > single_element_compression.abaqus_v6.env
   cd /home/roppenheimer/waves-eabm-tutorial/build/tutorial_escape_sequences && /apps/abaqus/Commands/abq2021 -job single_element_compression -input single_element_compression -double both -cpus 1 -interactive -ask_delete no > single_element_compression.stdout 2>&1
   scons: done building targets.

7. Execute the build command again with a different number of solve cpus. Observe that the workflow is reported as
   up-to-date.

.. code-block::

   $ pwd
   /path/to/waves-eabm-tutorial
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
   /home/roppenheimer/waves-eabm-tutorial
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
   |-- single_element_compression.abaqus_v6.env
   |-- single_element_compression.com
   |-- single_element_compression.dat
   |-- single_element_compression.inp
   |-- single_element_compression.msg
   |-- single_element_compression.odb
   |-- single_element_compression.prt
   |-- single_element_compression.sta
   |-- single_element_compression.stdout
   |-- single_element_geometry.abaqus_v6.env
   |-- single_element_geometry.cae
   |-- single_element_geometry.jnl
   |-- single_element_geometry.stdout
   |-- single_element_mesh.abaqus_v6.env
   |-- single_element_mesh.cae
   |-- single_element_mesh.inp
   |-- single_element_mesh.jnl
   |-- single_element_mesh.stdout
   |-- single_element_partition.abaqus_v6.env
   |-- single_element_partition.cae
   |-- single_element_partition.jnl
   `-- single_element_partition.stdout

   0 directories, 31 files
