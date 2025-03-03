.. _tutorial_simulation:

#######################
Tutorial 04: Simulation
#######################

**********
References
**********

* `Abaqus File Extension Definitions`_ :cite:`ABAQUS`
* `Abaqus Standard/Explicit Execution`_ :cite:`ABAQUS`
* `Abaqus Precision Level for Executables`_ :cite:`ABAQUS`

***********
Environment
***********

.. include:: tutorial_environment_activation.txt

.. include:: version_check_warning.txt

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
        $ waves fetch --overwrite --tutorial 3 && mv tutorial_03_solverprep_SConstruct SConstruct
        Destination directory: '/home/roppenheimer/waves-tutorials'

4. Fetch the ``tutorial_03_solverprep`` file and create a new file named ``tutorial_04_simulation``
   with the :ref:`waves_cli` :ref:`waves_fetch_cli` subcommand.

.. code-block:: bash

   $ pwd
   /home/roppenheimer/waves-tutorials
   $ waves fetch --overwrite tutorials/tutorial_03_solverprep && cp tutorial_03_solverprep tutorial_04_simulation
   WAVES fetch
   Destination directory: '/home/roppenheimer/waves-tutorials'

.. _tutorials_tutorial_simulation:

**********
SConscript
**********

.. note::

    There is a large section of lines in the ``SConscript`` file that are not included before the next section of code
    shown here, as they are identical to those from :ref:`tutorial_solverprep`. The ``diff`` of the ``SConscript``
    file at the end of the :ref:`tutorials_tutorial_simulation` section will demonstrate this more clearly.

.. _tutorial_simulation_waves_running_datacheck:


5. Add the highlighted section shown below to the ``tutorial_04_simulation`` file.
   This will initialize the datacheck list.

.. admonition:: waves-tutorials/tutorial_04_simulation

    .. literalinclude:: tutorials_tutorial_04_simulation
       :language: Python
       :lineno-match:
       :emphasize-lines: 3
       :start-after: marker-1
       :end-before: marker-2

6. Add the highlighted sections shown below to the ``tutorial_04_simulation`` file.
   This will create the datackeck alias.

.. admonition:: waves-tutorials/tutorial_04_simulation

    .. literalinclude:: tutorials_tutorial_04_simulation
       :language: Python
       :lineno-match:
       :emphasize-lines: 3,8
       :start-after: marker-6

Running a Datacheck
===================

7. Modify your ``tutorial_04_simulation`` file by adding the contents shown below immediately after the code
   pertaining to ``# SolverPrep`` from the previous tutorial.

.. admonition:: waves-tutorials/tutorial_04_simulation

    .. literalinclude:: tutorials_tutorial_04_simulation
       :language: Python
       :lineno-match:
       :start-after: marker-4
       :end-before: marker-5

The ``solve_source_list`` variable looks similar to the solver prep list added in :ref:`tutorial_solverprep`. There are
two important differences. First, the solve source list uses the file basenames. The solver prep task copied the
necessary Abaqus input files into the build directory. When we refer to the file basenames, SCons will know to look for
the copy in the current build directory. Second, the ``rectangle_mesh.inp`` file has been added to the end of the solve
source list. This is the mesh file produced by the mesh task defined in :ref:`tutorial_partition_mesh`.

The code snippet will define an optional task called a *datacheck*. You can read the `Abaqus Standard/Explicit
Execution`_ documentation :cite:`ABAQUS` for more details on running a datacheck. The primary purpose for running a
datacheck is to verify the input file construction without running a full simulation. While Abaqus can continue with an
analysis from the datacheck output, doing so modifies the datacheck output files, which has the affect of prompting
`SCons`_ to always re-build the datacheck target. This task is excluded from the main ``workflow`` to avoid duplicate
preprocessing of the input file. It will be used later in :ref:`tutorial_regression_testing`.

One new section of code that we have not utilized yet in the previous tutorials is the passing of command-line options
to the builder. This is done using the ``program_options`` variable. Here, we instruct the Abaqus solver to use double
precision for both the packager and the analysis. See the `Abaqus Precision Level for Executables`_ documentation
:cite:`ABAQUS` for more information about the use of single or double precision in an Abaqus analysis.

The ``solve_source_list`` and target lists are hardcoded for clarity in the tutorials. Python users familiar with list
comprehensions and the ``pathlib`` module should be able to construct the ``solve_source_list`` from the
``copy_source_list`` introduced in :ref:`tutorial_solverprep`. Similarly, the datacheck target list could be constructed
from a list comprehension and Python f-strings.

.. _tutorial_simulation_waves_running_analysis:

Running the Analysis
====================

8. Modify your ``tutorial_04_simulation`` file by adding the contents below immediately after the Abaqus
   datacheck code that was just discussed.

.. admonition:: waves-tutorials/tutorial_04_simulation

    .. literalinclude:: tutorials_tutorial_04_simulation
       :language: Python
       :lineno-match:
       :start-after: marker-5
       :end-before: marker-6

The changes you just made will be used to define the task for running the ``rectangle_compression`` analysis.

The next step should now be quite familiar - we extend the ``workflow`` list to include that task for running the
simulation with the :meth:`waves.scons_extensions.abaqus_solver_builder_factory` builder. The ``source`` list uses the
existing ``solve_source_list`` variable because the datacheck and solve tasks share the same dependencies. The ``job``
task keyword argument has dropped the ``DATACHECK`` suffix. The ``-double both`` option is included with the
``program_options`` variable.

The ``program_options`` are again hardcoded for clarity in the tutorials, but Python users may have identified this as
an opportunity to collect the common datacheck and solve task options in a common variable to ensure consistency in
Abaqus options.

In summary of the changes you just made to the ``tutorial_04_simulation`` file, a ``diff`` against the ``SConscript``
file from :ref:`tutorial_solverprep` is included below to help identify the changes made in this tutorial. Note the
addition of a separate datacheck alias, which will be used in :ref:`tutorial_regression_testing`.

.. admonition:: waves-tutorials/tutorial_04_simulation

   .. literalinclude:: tutorials_tutorial_04_simulation
      :language: Python
      :diff: tutorials_tutorial_03_solverprep

**********
SConstruct
**********

9. Add ``tutorial_04_simulation`` to the ``workflow_configurations`` list in the ``SConstruct`` file.

A ``diff`` against the ``SConstruct`` file from :ref:`tutorial_solverprep` is included below to help identify the
changes made in this tutorial.

.. admonition:: waves-tutorials/SConstruct

   .. literalinclude:: tutorials_tutorial_04_simulation_SConstruct
      :language: Python
      :diff: tutorials_tutorial_03_solverprep_SConstruct

*************
Build Targets
*************

10. Build the new targets

.. code-block:: bash

   $ pwd
   /home/roppenheimer/waves-tutorials
   $ scons tutorial_04_simulation
   scons: Reading SConscript files ...
   Checking whether /apps/abaqus/Commands/abq2024 program exists.../apps/abaqus/Commands/abq2024
   Checking whether abq2024 program exists.../apps/abaqus/Commands/abq2024
   scons: done reading SConscript files.
   scons: Building targets ...
   cd /home/roppenheimer/waves-tutorials/build/tutorial_04_simulation && /apps/abaqus/Commands/abq2024 cae -noGui /home/roppenheimer/waves-tutorials/modsim_package/abaqus/rectangle_geometry.py -- > rectangle_geometry.stdout 2>&1
   cd /home/roppenheimer/waves-tutorials/build/tutorial_04_simulation && /apps/abaqus/Commands/abq2024 cae -noGui /home/roppenheimer/waves-tutorials/modsim_package/abaqus/rectangle_partition.py -- > rectangle_partition.stdout 2>&1
   cd /home/roppenheimer/waves-tutorials/build/tutorial_04_simulation && /apps/abaqus/Commands/abq2024 cae -noGui /home/roppenheimer/waves-tutorials/modsim_package/abaqus/rectangle_mesh.py -- > rectangle_mesh.stdout 2>&1
   Copy("build/tutorial_04_simulation/rectangle_compression.inp", "modsim_package/abaqus/rectangle_compression.inp")
   Copy("build/tutorial_04_simulation/assembly.inp", "modsim_package/abaqus/assembly.inp")
   Copy("build/tutorial_04_simulation/boundary.inp", "modsim_package/abaqus/boundary.inp")
   Copy("build/tutorial_04_simulation/field_output.inp", "modsim_package/abaqus/field_output.inp")
   Copy("build/tutorial_04_simulation/materials.inp", "modsim_package/abaqus/materials.inp")
   Copy("build/tutorial_04_simulation/parts.inp", "modsim_package/abaqus/parts.inp")
   Copy("build/tutorial_04_simulation/history_output.inp", "modsim_package/abaqus/history_output.inp")
   cd /home/roppenheimer/waves-tutorials/build/tutorial_04_simulation && /apps/abaqus/Commands/abq2024 -job rectangle_compression -input rectangle_compression -double both -interactive -ask_delete no > rectangle_compression.stdout 2>&1
   scons: done building targets.

************
Output Files
************

Explore the contents of the ``build`` directory using the ``tree`` command against the ``build`` directory, as shown
below.

.. code-block:: bash

    $ pwd
    /home/roppenheimer/waves-tutorials
    $ tree build/tutorial_04_simulation/
    build/tutorial_04_simulation/
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
    |-- rectangle_geometry.cae.stdout
    |-- rectangle_geometry.jnl
    |-- rectangle_mesh.cae
    |-- rectangle_mesh.inp
    |-- rectangle_mesh.inp.stdout
    |-- rectangle_mesh.jnl
    |-- rectangle_partition.cae
    |-- rectangle_partition.cae.stdout
    `-- rectangle_partition.jnl

    0 directories, 27 files

The ``build/tutorial_04_simulation`` directory contains several different subsets of related files:

* ``rectangle_{geometry,partition,mesh}.*`` - output files generated from the code pertaining to ``# Geometry``,
  ``# Partition``, and ``# Mesh`` in the ``SConscript`` file. This code was first introduced in
  :ref:`tutorial_geometry` and :ref:`tutorial_partition_mesh`, but it is important to note that each
  tutorial adds and executes a full workflow.
* ``*.inp`` - files copied to the build directory as part of the code pertaining to ``# SolverPrep`` in the
  ``SConscript`` file, which was introduced in :ref:`tutorial_solverprep`.
* ``rectangle_compression.*`` - output files from :ref:`tutorial_simulation_waves_running_analysis` in this
  tutorial.

**********************
Workflow Visualization
**********************

View the workflow directed graph by running the following command and opening the image in your preferred image viewer.

.. code-block::

   $ pwd
   /home/roppenheimer/waves-tutorials
   $ waves visualize tutorial_04_simulation --output-file tutorial_04_simulation.png --width=28 --height=5 --exclude-list /usr/bin .stdout .jnl .prt .com

The output should look similar to the figure below.

.. raw:: latex

    \begin{landscape}
        \vspace*{\fill}

.. figure:: tutorial_04_simulation.png
   :align: center
   :width: 100%

.. raw:: latex

        \vspace*{\fill}
    \end{landscape}
