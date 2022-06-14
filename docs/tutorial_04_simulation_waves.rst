.. _tutorial_simulation_waves:

#######################
Tutorial 04: Simulation
#######################

**********
References
**********

* `Abaqus File Extension Definitions`_
* `Abaqus Standard/Explicit Execution`_
* `Abaqus Precision Level for Executables`_

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
       :start-after: marker-1
       :end-before: marker-2
       :emphasize-lines: 4-12

In the changes you just made, the first line of code removes any trailing ``.in`` extensions from the file names in the 
``abaqus_source_list`` (which you defined in the previous tutorial). While this step is not strictly neccessary for this 
tutorial, it is required when it comes to substituting parameters into files. This is discussed in detail in the next 
tutorial, :ref:`tutorial_parameter_substitution_waves`.

Next, ``{journal_file}.inp`` needs to be appended to the list of simulation source files. Recall from 
:ref:`tutorial_partition_mesh_waves` that this file is one of the targets that is generated from  
:meth:`waves.builders.abaqus_journal` builder in the code pertaining to ``# Mesh``.

The first set of highlighted lines will define a prelimnary step to the actual analysis called a *datacheck*. You can 
read the `Abaqus Standard/Explicit Execution`_ documentation for more details on running a datacheck. First, the 
``job_name`` is resolved from the name of the first source file listed in code pertaining to ``# SolverPrep``, in this 
case ``single_element_compression``. That name is appened with the ``_DATACHECK`` string to uniquely identify output 
files that might have common name and extension with those from the actual analysis to come. The ``datacheck_suffixes`` 
are standard output file extensions that will form the targets of our datacheck task. See the `Abaqus File Extension 
Definitions`_ documentation for more information about each of the file extensions listed.

One new section of code that we have not utilized yet in the previous tutotorials is the passing of command line options 
to the builder. This is done using the ``abaqus_options`` variable. Here, we instruct the Abaqus solver to use double 
precision for both the packager and the analysis. See the `Abaqus Precision Level for Executables`_ documentation for 
more information about the use of single or double precision in an Abaqus analysis.

Finally, the ``workflow`` list is extended to define the task for running the datacheck. The ``target`` list is formed 
by adding the ``datacheck_suffixes`` to the ``datacheck_name``. The ``source`` list was created in the first portions of 
the new code for this tutorial. ``job_name`` is used in the Abaqus solver call. See the 
:meth:`waves.builders.abaqus_solver` API for information about default behavior. Lastly, the ``abaqus_options`` are 
passed to the builder to be appended to the Abaqus solver call.

.. _tutorial_simulation_waves_running_analysis:

Running the Analysis
====================

6. Modify your ``tutorial_04_simulation/SConscript`` file by adding the contents below immediately after the Abaqus 
   datacheck code that was just discussed.

.. admonition:: waves-eabm-tutorial/tutorial_04_simulation/SConscript

    .. literalinclude:: tutorial_04_simulation_SConscript
       :language: Python
       :lineno-match:
       :start-after: marker-2
       :end-before: marker-3

The changes you just made will be used to define the task for running the ``single_element_compression`` analysis. 
Before running the analysis, we must first ensure that the output from the datacheck is included in the 
``solve_source_list``. Appending the ``{datacheck_name}.odb`` file to the list of source files ensures that Abaqus 
solver effort is not duplicated between the datacheck and the analysis we are about to run.

The next step should now be quite familiar - we extend the ``workflow`` list to include that task for running the 
simulation with the :meth:`waves.builders.abaqus_solver` builder. The ``target`` list includes only the 
``{job_name}.sta`` file, though many more output files will be generated by the Abaqus solver. As discussed in the 
:meth:`waves.builders.abaqus_solver` API, there is a default list of targets that will be appended to the ``target`` 
list by the builder. The ``source`` list once again utlizes the existing ``solve_source_list`` variable, and the 
``job_name`` now uses the ``job_name`` variable that was defined at the beginning of this tutorial. Lasly, the ``-double 
both`` option is included with the ``abaqus_options`` variable.

.. note::
    
    The :meth:`waves.builders.solve_abaqus` builder has the option to retrieve non-zero exit codes from the Abaqus 
    solver by parsing the output ``.sta`` file using ``grep``. The :meth:`waves.builders.solve_abaqus` API provides and 
    example of the ``post_simulation`` builder argument as well as how exit codes are returned to the build system.

    This functionality is useful in cases where the model developer wants the build system to exit its processes if an 
    Abaqus analysis does not complete successfully. By default, Abaqus will return a zero exit code regradless of 
    analysis success, and the build system will continue to build targets. If an analysis fails, the source files which 
    are required to build certain targets may not exist, which will also cause the build system to fail.

In summary of the changes you just made to the ``tutorial_04_simulation/SConscript`` file, a ``diff`` against the 
``SConscript`` file from :ref:`tutorial_solverprep_waves` is included below to help identify the changes made in this 
tutorial.

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
    /projects/aea_compute/aea-beta/lib/python3.8/site-packages/setuptools_scm/version.py:74: UserWarning: tag '0.1.10+dev' will 
    be stripped of its suffix '+dev'
      warnings.warn(
    Checking whether sphinx-build program exists.../projects/aea_compute/aea-beta/bin/sphinx-build
    Checking whether abaqus program exists.../apps/abaqus/Commands/abaqus
    Checking whether cubit program exists.../apps/Cubit-15.8/cubit
    scons: done reading SConscript files.
    scons: Building targets ...
    cd /home/roppenheimer/waves-eabm-tutorial/tutorial_04_simulation && /apps/abaqus/Commands/abaqus -information environment 
    > single_element_geometry.abaqus_v6.env
    cd /home/roppenheimer/waves-eabm-tutorial/tutorial_04_simulation && /apps/abaqus/Commands/abaqus cae -noGui 
    /home/roppenheimer/waves-eabm-tutorial/eabm_package/abaqus/single_element_geometry.py -- > single_element_geometry.stdout 2>&1
    cd /home/roppenheimer/waves-eabm-tutorial/tutorial_04_simulation && /apps/abaqus/Commands/abaqus -information environment 
    > single_element_partition.abaqus_v6.env
    cd /home/roppenheimer/waves-eabm-tutorial/tutorial_04_simulation && /apps/abaqus/Commands/abaqus cae -noGui 
    /home/roppenheimer/waves-eabm-tutorial/eabm_package/abaqus/single_element_partition.py -- > single_element_partition.stdout 2>&1
    cd /home/roppenheimer/waves-eabm-tutorial/tutorial_04_simulation && /apps/abaqus/Commands/abaqus -information environment 
    > single_element_mesh.abaqus_v6.env
    cd /home/roppenheimer/waves-eabm-tutorial/tutorial_04_simulation && /apps/abaqus/Commands/abaqus cae -noGui 
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
    cd /home/roppenheimer/waves-eabm-tutorial/tutorial_04_simulation && /apps/abaqus/Commands/abaqus -information environment 
    > single_element_compression_DATACHECK.abaqus_v6.env
    cd /home/roppenheimer/waves-eabm-tutorial/tutorial_04_simulation && /apps/abaqus/Commands/abaqus -job 
    single_element_compression_DATACHECK -input single_element_compression -double both -datacheck -interactive -ask_delete 
    no > single_element_compression_DATACHECK.stdout 2>&1
    cd /home/roppenheimer/waves-eabm-tutorial/tutorial_04_simulation && ! grep -iE "error" 
    single_element_compression_DATACHECK.stdout
    cd /home/roppenheimer/waves-eabm-tutorial/tutorial_04_simulation && /apps/abaqus/Commands/abaqus -information environment 
    > single_element_compression.abaqus_v6.env
    cd /home/roppenheimer/waves-eabm-tutorial/tutorial_04_simulation && /apps/abaqus/Commands/abaqus -job 
    single_element_compression -input single_element_compression -double both -interactive -ask_delete no > 
    single_element_compression.stdout 2>&1
    cd /home/roppenheimer/waves-eabm-tutorial/tutorial_04_simulation && ! grep -iE "error" single_element_compression.stdout
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
    $ tree build/ -I 'tutorial[1,2,3]*'
    build
    ├── docs
    │   └── SConscript
    └── tutorial_04_simulation
        ├── abaqus.rpy
        ├── abaqus.rpy.1
        ├── abaqus.rpy.2
        ├── amplitudes.inp
        ├── assembly.inp
        ├── boundary.inp
        ├── field_output.inp
        ├── history_output.inp
        ├── materials.inp
        ├── parts.inp
        ├── single_element_compression.abaqus_v6.env
        ├── single_element_compression.com
        ├── single_element_compression.dat
        ├── single_element_compression_DATACHECK.023
        ├── single_element_compression_DATACHECK.abaqus_v6.env
        ├── single_element_compression_DATACHECK.com
        ├── single_element_compression_DATACHECK.dat
        ├── single_element_compression_DATACHECK.mdl
        ├── single_element_compression_DATACHECK.msg
        ├── single_element_compression_DATACHECK.odb
        ├── single_element_compression_DATACHECK.prt
        ├── single_element_compression_DATACHECK.sim
        ├── single_element_compression_DATACHECK.stdout
        ├── single_element_compression_DATACHECK.stt
        ├── single_element_compression.inp
        ├── single_element_compression.msg
        ├── single_element_compression.odb
        ├── single_element_compression.prt
        ├── single_element_compression.sta
        ├── single_element_compression.stdout
        ├── single_element_geometry.abaqus_v6.env
        ├── single_element_geometry.cae
        ├── single_element_geometry.jnl
        ├── single_element_geometry.stdout
        ├── single_element_mesh.abaqus_v6.env
        ├── single_element_mesh.cae
        ├── single_element_mesh.inp
        ├── single_element_mesh.jnl
        ├── single_element_mesh.stdout
        ├── single_element_partition.abaqus_v6.env
        ├── single_element_partition.cae
        ├── single_element_partition.jnl
        └── single_element_partition.stdout

    2 directories, 44 files

The ``tutorial_04_simulation`` directory contains several different subsets of related files:

* ``single_element_geometry.*``, ``_partition.*``, and ``_mesh.*`` - output files generated from the workflow in 
  :ref:`tutorial_geometry_waves` and :ref:`tutorial_partition_mesh_waves`.
* ``*.inp`` - files copied to the build directory as part of :ref:`tutorial_solverprep_waves`.
* ``single_element_compression_DATACHECK.*`` - output files from :ref:`tutorial_simulation_waves_running_datacheck`.
* ``single_element_compression.*`` - output files from :ref:`tutorial_simulation_waves_running_analysis`.

