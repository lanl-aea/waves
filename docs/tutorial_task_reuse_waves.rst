.. _tutorial_task_reuse_waves:

################################
Tutorial: Task Definition Re-use
################################

.. include:: wip_warning.txt

This tutorial demonstrates one solution to re-using task definitions in multiple workflows. While the solution can be
implemented with per-task granularity, the task definitions in this tutorial are split into blocks to suite the
parameterization workflows of :ref:`tutorial_cartesian_product_waves` and :ref:`tutorial_mesh_convergence_waves`.

The presented solution comes with significant restrictions to directory organization and challenges to target node
identification. First, due to the way `SCons`_ constructs variant (build) directory directed graphs, the re-usable
portions of the workflow must be co-located with the calling file or found in a subdirectory. The choice of organization
has implications for the build directory organization options, too. For example, the two possible directory organization
may look like one of

.. code-block:: bash

   project directory/
   |-- SConscruct
   |-- workflow1
   |-- workflow2
   |-- common
   `-- build directory/
       |-- workflow1 directory/
       |   |-- workflow1 output
       |   |-- common1 output
       `-- workflow2 directory*
           |-- workflow2 output
           `-- common2 output

.. code-block:: bash

   project directory/
   |-- SConscruct
   |-- workflow1
   |-- workflow2
   |-- common directory/
   |   `-- common
   `-- build directory/
       |-- workflow1 directory/
       |   |-- workflow1 output
       |   `-- common directory/
       |       `-- common1 output
       `-- workflow2 directory/
           |-- workflow2 output
           `-- common directory/
               `-- common2 output

Second, if a target from the parent file is used as a source in the common file, `SCons`_ will recognize the build path
correctly when provided with the target file base name, but it may not associate the source and target nodes correctly.
This results in an incorrectly assembled directed graph and race conditions in the task execution. The target/source
association may be made explicit with the `SCons FindFile`_ function. While this works, it is not as straightforward as
simply specifying the file basename, as implemented in the core tutorials. This second restriction does not affect the
current tutorial, but will affect workflows similar to the :ref:`tutorial_mesh_convergence_waves`.

**********
References
**********

* `SCons FindFile`_ :cite:`scons-user`

***********
Environment
***********

.. include:: tutorial_environment_activation.txt

*******************
Directory Structure
*******************

3. Copy the ``tutorial_10_regression_testing`` file into a new file named ``tutorial_task_reuse``

.. code-block:: bash

   $ pwd
   /path/to/waves-eabm-tutorial
   $ cp tutorial_10_regression_testing tutorial_task_reuse

**********
SConscript
**********

A ``diff`` against the ``SConscript`` file from :ref:`tutorial_regression_testing_waves` is included below to help identify the
changes made in this tutorial.

.. admonition:: waves-eabm-tutorial/tutorial_task_reuse

   .. literalinclude:: tutorials_tutorial_task_reuse
      :language: Python
      :diff: tutorials_tutorial_10_regression_testing

4. Create a new file named ``single_element_geometry_partition.scons`` from the contents below

.. admonition:: waves-eabm-tutorial/single_element_geometry_partition.scons

   .. literalinclude:: tutorials_single_element_geometry_partition.scons
      :language: Python
      :lineno-match:

5. Create a new file named ``single_element_mesh_solverprep_solve_extract.scons`` from the contents below

.. admonition:: waves-eabm-tutorial/single_element_mesh_solverprep_solve_extract.scons

   .. literalinclude:: tutorials_single_element_mesh_solverprep_solve_extract.scons
      :language: Python
      :lineno-match:

**********
SConstruct
**********

A ``diff`` against the ``SConstruct`` file from :ref:`tutorial_regression_testing_waves` is included below to help identify the
changes made in this tutorial.

.. admonition:: waves-eabm-tutorial/SConstruct

   .. literalinclude:: tutorials_tutorial_task_reuse_SConstruct
      :language: Python
      :diff: tutorials_tutorial_10_regression_testing_SConstruct

*************
Build Targets
*************

6. Build the new targets

.. code-block:: bash

   $ pwd
   /path/to/waves-eabm-tutorial
   $ scons tutorial_task_reuse --jobs=4

************
Output Files
************

.. code-block:: bash

   $ pwd
   /path/to/waves-eabm-tutorial
   $ tree build/tutorial_task_reuse/parameter_set0/
   build/tutorial_task_reuse/parameter_set0/
   |-- abaqus.rpy
   |-- abaqus.rpy.1
   |-- abaqus.rpy.2
   |-- assembly.inp
   |-- boundary.inp
   |-- field_output.inp
   |-- history_output.inp
   |-- materials.inp
   |-- parts.inp
   |-- single_element_compression.inp
   |-- single_element_compression.inp.in
   |-- single_element_compression_DATACHECK.023
   |-- single_element_compression_DATACHECK.abaqus_v6.env
   |-- single_element_compression_DATACHECK.com
   |-- single_element_compression_DATACHECK.dat
   |-- single_element_compression_DATACHECK.mdl
   |-- single_element_compression_DATACHECK.msg
   |-- single_element_compression_DATACHECK.odb
   |-- single_element_compression_DATACHECK.prt
   |-- single_element_compression_DATACHECK.sim
   |-- single_element_compression_DATACHECK.stdout
   |-- single_element_compression_DATACHECK.stt
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

   0 directories, 35 files
