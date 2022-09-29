.. _tutorial_simulation_waves:

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

*******************
Directory Structure
*******************

3. Create a directory ``tutorial_04_simulation`` in the ``waves-eabm-tutorial`` directory.

.. code-block:: bash

   $ pwd
   /path/to/waves-eabm-tutorial
   $ mkdir tutorial_04_simulation

4. Copy the ``tutorial_03_solverprep/SConscript`` file into the newly created ``tutorial_04_simulation``
   directory.

.. code-block:: bash

   $ pwd
   /path/to/waves-eabm-tutorial
   $ cp tutorial_03_solverprep/SConscript tutorial_04_simulation/


.. _tutorial_simulation_waves_SConscript:

**********
SConscript
**********

.. note::

    There is a large section of lines in the ``SConscript`` file that are not included before the next section of code
    shown here, as they are identical to those from :ref:`tutorial_solverprep_waves`. The ``diff`` of the ``SConscript``
    file at the end of the :ref:`tutorial_simulation_waves_SConscript` section will demonstrate this more clearly.

.. _tutorial_simulation_waves_running_datacheck:

Running a Datacheck
===================

5. Modify your ``tutorial_04_simulation/SConscript`` file by adding the contents shown below immediately after the code
   pertaining to ``# SolverPrep`` from the previous tutorial.

.. admonition:: waves-eabm-tutorial/tutorial_04_simulation/SConscript

    .. literalinclude:: tutorial_04_simulation_SConscript
       :language: Python
       :lineno-match:
       :start-after: marker-4
       :end-before: marker-5
       :emphasize-lines: 4-12

In the changes you just made, the first line of code extracts the file ``name`` from the `Python pathlib`_ objects in 
the ``abaqus_source_list`` (which you defined in the previous tutorial) and removes any trailing ``.in`` extensions from 
the file names. The ``pathlib.Path.name`` method strips the leading path from the `Python pathlib`_ object and leaves 
the file name, for example 

.. code-block:: Python
    
    >>> source_file = pathlib.Path('/path/to/file.extension')
    >>> print(type(source_file), str(source_file))
    <class 'pathlib.PosixPath'> /path/to/file.extension
    >>> print(type(source_file.name), source_file.name)
    <class 'str'> file.extension

In this tutorial, there are no files with ``.in`` extension; this is required when it comes to substituting parameters 
into files which is discussed in the next tutorial,
:ref:`tutorial_parameter_substitution_waves`. For this tutorial, we only require that the file names be extracted from
the ``abaqus_source_list``. This tutorial would behave identically if the ``solve_source_list`` was defined as

.. code-block:: Python
    
    solve_source_list = [source_file.name for source_file in abaqus_source_list]

Next, ``{journal_file}.inp`` needs to be appended to the list of simulation source files. Recall from
:ref:`tutorial_partition_mesh_waves` that this file is one of the targets that is generated from
:meth:`waves.builders.abaqus_journal` builder in the code pertaining to ``# Mesh``.

The first set of highlighted lines will define an optional task called a *datacheck*. You can read the `Abaqus
Standard/Explicit Execution`_ documentation :cite:`ABAQUS` for more details on running a datacheck. The primary purpose
for running a datacheck is to verify the input file construction without running a full simulation. While Abaqus can
continue with an analysis from the datacheck output, doing so modifies the datacheck output files, which has the affect
of prompting `SCons`_ to always re-build the datacheck target. This task is excluded from the main workflow to avoid
duplicate preprocessing of the input file. It will be used later in :ref:`tutorial_regression_testing_waves`.

First, the ``job_name`` is resolved from the name of the first source file listed in code pertaining to ``#
SolverPrep``, in this case ``single_element_compression``. That name is appended with the ``_DATACHECK`` string to
uniquely identify output files that might have a common name and extension with those from the actual analysis to come.
The ``datacheck_suffixes`` are standard output file extensions that will form the targets of our datacheck task. See the
`Abaqus File Extension Definitions`_ documentation :cite:`ABAQUS` for more information about each of the file
extensions listed.

One new section of code that we have not utilized yet in the previous tutotorials is the passing of command line options
to the builder. This is done using the ``abaqus_options`` variable. Here, we instruct the Abaqus solver to use double
precision for both the packager and the analysis. See the `Abaqus Precision Level for Executables`_ documentation
:cite:`ABAQUS` for more information about the use of single or double precision in an Abaqus analysis.

Finally, the ``datacheck`` list is extended separately from the ``workflow`` list to separate the task for running the
datacheck from the full simulation workflow. The ``target`` list is formed by adding the ``datacheck_suffixes`` to the
``datacheck_name``. The ``source`` list was created in the first portions of the new code for this tutorial.
``job_name`` is used in the Abaqus solver call. See the :meth:`waves.builders.abaqus_solver` API for information about
default behavior. Lastly, the ``abaqus_options`` are passed to the builder to be appended to the Abaqus solver call.

.. _tutorial_simulation_waves_running_analysis:

Running the Analysis
====================

6. Modify your ``tutorial_04_simulation/SConscript`` file by adding the contents below immediately after the Abaqus
   datacheck code that was just discussed.

.. admonition:: waves-eabm-tutorial/tutorial_04_simulation/SConscript

    .. literalinclude:: tutorial_04_simulation_SConscript
       :language: Python
       :lineno-match:
       :start-after: marker-5
       :end-before: marker-6

The changes you just made will be used to define the task for running the ``single_element_compression`` analysis.
Before running the analysis, we add the output from the datacheck to the ``solve_source_list``. Appending the
``{datacheck_name}.odb`` file to the list of source files ensures that the simulation targets are rebuilt if something
in the datacheck outputs changes. The build system will recognize this dependency automatically, so long as
``{datacheck_name}.odb`` is defined as a source.

The next step should now be quite familiar - we extend the ``workflow`` list to include that task for running the
simulation with the :meth:`waves.builders.abaqus_solver` builder. The ``target`` list includes only the
``{job_name}.sta`` file, though many more output files will be generated by the Abaqus solver. As discussed in the
:meth:`waves.builders.abaqus_solver` API, there is a default list of targets that will be appended to the ``target``
list by the builder. The ``source`` list once again utlizes the existing ``solve_source_list`` variable, and the
``job_name`` now uses the ``job_name`` variable that was defined at the beginning of this tutorial. Lastly, the
``-double both`` option is included with the ``abaqus_options`` variable.

.. note::

    The :meth:`waves.builders.solve_abaqus` builder has the option to retrieve non-zero exit codes from the Abaqus
    solver by parsing the output ``.sta`` file using ``grep``. The :meth:`waves.builders.solve_abaqus` API provides and
    example of the ``post_simulation`` builder argument as well as how exit codes are returned to the build system.

    This functionality is useful in cases where the model developer wants the build system to exit its processes if an
    Abaqus analysis does not complete successfully. By default, Abaqus will return a zero exit code regardless of
    analysis success, and the build system will continue to build targets. If an analysis fails, the source files which
    are required to build certain targets may not exist, which will also cause the build system to fail.

In summary of the changes you just made to the ``tutorial_04_simulation/SConscript`` file, a ``diff`` against the
``SConscript`` file from :ref:`tutorial_solverprep_waves` is included below to help identify the changes made in this
tutorial. Note the addition of a separate datacheck alias, which will be used in
:ref:`tutorial_regression_testing_waves`.

.. admonition:: waves-eabm-tutorial/tutorial_04_simulation/SConscript

   .. literalinclude:: tutorial_04_simulation_SConscript
      :language: Python
      :diff: tutorial_03_solverprep_SConscript

**********
SConstruct
**********

7. Make the following additions to the ``waves-eabm-tutorial/SConstruct`` file using the ``diff`` against the
   ``SConstruct`` file from the last tutorial:

   * Add the ``AbaqusSolver`` key-value pair to the ``BUILDERS`` dictionary in the code beneath ``# Add custom
     builders``
   * Add ``tutorial_04_simulation`` to the ``eabm_simulation_directories`` list

A ``diff`` against the ``SConstruct`` file from :ref:`tutorial_solverprep_waves` is included below to help identify the
changes made in this tutorial.

.. admonition:: waves-eabm-tutorial/SConstruct

   .. literalinclude:: eabm_tutorial_04_simulation_SConstruct
      :language: Python
      :diff: eabm_tutorial_03_solverprep_SConstruct

*************
Build Targets
*************

5. Build the new targets

.. code-block:: bash

   $ pwd
   /path/to/waves-eabm-tutorial
   $ scons tutorial_04_simulation
   scons: Reading SConscript files ...
   Checking whether abq2021 program exists.../apps/abaqus/Commands/abq2021
   Checking whether abq2020 program exists.../apps/abaqus/Commands/abq2020
   scons: done reading SConscript files.
   scons: Building targets ...
   cd /home/roppenheimer/waves-eabm-tutorial/build/tutorial_04_simulation && /apps/abaqus/Commands/abaqus -information environment
   > single_element_geometry.abaqus_v6.env
   cd /home/roppenheimer/waves-eabm-tutorial/build/tutorial_04_simulation && /apps/abaqus/Commands/abaqus cae -noGui
   /home/roppenheimer/waves-eabm-tutorial/eabm_package/abaqus/single_element_geometry.py -- > single_element_geometry.stdout 2>&1
   cd /home/roppenheimer/waves-eabm-tutorial/build/tutorial_04_simulation && /apps/abaqus/Commands/abaqus -information
   environment > single_element_partition.abaqus_v6.env
   cd /home/roppenheimer/waves-eabm-tutorial/build/tutorial_04_simulation && /apps/abaqus/Commands/abaqus cae -noGui
   /home/roppenheimer/waves-eabm-tutorial/eabm_package/abaqus/single_element_partition.py -- > single_element_partition.stdout 2>&1
   cd /home/roppenheimer/waves-eabm-tutorial/build/tutorial_04_simulation && /apps/abaqus/Commands/abaqus -information environment
   > single_element_mesh.abaqus_v6.env
   cd /home/roppenheimer/waves-eabm-tutorial/build/tutorial_04_simulation && /apps/abaqus/Commands/abaqus cae -noGui
   /home/roppenheimer/waves-eabm-tutorial/eabm_package/abaqus/single_element_mesh.py -- > single_element_mesh.stdout 2>&1
   Copy("build/tutorial_04_simulation/single_element_compression.inp",
   "eabm_package/abaqus/single_element_compression.inp")
   Copy("build/tutorial_04_simulation/amplitudes.inp", "eabm_package/abaqus/amplitudes.inp")
   Copy("build/tutorial_04_simulation/assembly.inp", "eabm_package/abaqus/assembly.inp")
   Copy("build/tutorial_04_simulation/boundary.inp", "eabm_package/abaqus/boundary.inp")
   Copy("build/tutorial_04_simulation/field_output.inp", "eabm_package/abaqus/field_output.inp")
   Copy("build/tutorial_04_simulation/materials.inp", "eabm_package/abaqus/materials.inp")
   Copy("build/tutorial_04_simulation/parts.inp", "eabm_package/abaqus/parts.inp")
   Copy("build/tutorial_04_simulation/history_output.inp", "eabm_package/abaqus/history_output.inp")
   cd /home/roppenheimer/waves-eabm-tutorial/build/tutorial_04_simulation && /apps/abaqus/Commands/abaqus -information environment
   > single_element_compression.abaqus_v6.env
   cd /home/roppenheimer/waves-eabm-tutorial/build/tutorial_04_simulation && /apps/abaqus/Commands/abaqus -job
   single_element_compression -input single_element_compression -double both -interactive -ask_delete no >
   single_element_compression.stdout 2>&1
   scons: done building targets.

************
Output Files
************

Explore the contents of the ``build`` directory using the ``tree`` command against the ``build`` directory, as shown
below. Note that the output files from the previous tutorials also exist in the ``build`` directory, but the ``-I``
option is used in the ``tree`` command below to reduce clutter in the ouptut shown.

.. code-block:: bash

    $ pwd
    /home/roppenheimer/waves-eabm-tutorial
    $ tree build/tutorial_04_simulation/
    build/tutorial_04_simulation/
    |-- abaqus.rpy
    |-- abaqus.rpy.1
    |-- abaqus.rpy.2
    |-- amplitudes.inp
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

    0 directories, 32 files

The ``tutorial_04_simulation`` directory contains several different subsets of related files:

* ``single_element_{geometry,partition,mesh}.*`` - output files generated from the code pertaining to ``# Geometry``,
  ``# Partition``, and ``# Mesh`` in the ``SConscript`` file. This code was first introduced in
  :ref:`tutorial_geometry_waves` and :ref:`tutorial_partition_mesh_waves`, but it is important to note that each
  tutorial adds and executes a full workflow.
* ``*.inp`` - files copied to the build directory as part of the code pertaining to ``# SolverPrep`` in the
  ``SConscript`` file, which was introduced in :ref:`tutorial_solverprep_waves`.
* ``single_element_compression.*`` - output files from :ref:`tutorial_simulation_waves_running_analysis` in this
  tutorial.
