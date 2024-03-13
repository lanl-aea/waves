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

.. include:: tutorial_directory_setup.txt

.. note::

    If you skipped any of the previous tutorials, run the following commands to create a copy of the necessary tutorial
    files.

    .. code-block:: bash

        $ pwd
        /home/roppenheimer/waves-tutorials
        $ waves fetch --overwrite --destination eabm_package tutorials/eabm_package/__init__.py
        WAVES fetch
        Destination directory: 'eabm_package'
        $ waves fetch --overwrite --destination eabm_package/abaqus 'tutorials/eabm_package/abaqus/*'
        WAVES fetch
        Destination directory: 'eabm_package/abaqus'
        $ waves fetch --overwrite --destination eabm_package/python 'tutorials/eabm_package/python/__init__.py' 'tutorials/eabm_package/python/rectangle_compression_nominal.py' 'tutorials/eabm_package/python/rectangle_compression_cartesian_product.py' 'tutorials/eabm_package/python/post_processing.py' 'tutorials/eabm_package/python/rectangle_compression_cartesian_product.csv'
        WAVES fetch
        Destination directory: 'eabm_package/python'
        $ waves fetch --overwrite 'tutorials/tutorial_01_geometry' 'tutorials/tutorial_02_partition_mesh' 'tutorials/tutorial_03_solverprep' 'tutorials/tutorial_04_simulation' 'tutorials/tutorial_05_parameter_substitution' 'tutorials/tutorial_06_include_files' 'tutorials/tutorial_07_cartesian_product' 'tutorials/tutorial_08_data_extraction' 'tutorials/tutorial_09_post_processing' 'tutorials/unit_testing' 'tutorials/tutorial_11_regression_testing'
        WAVES fetch
        Destination directory: '/home/roppenheimer/waves-tutorials'
        $ waves fetch tutorials/tutorial_12_archival_SConstruct && mv tutorial_12_archival_SConstruct SConstruct
        WAVES fetch
        Destination directory: '/home/roppenheimer/waves-tutorials'

4. Download and copy the ``tutorial_12_archival`` file to a new file named ``tutorial_task_reuse``
   with the :ref:`waves_cli` :ref:`waves_fetch_cli` subcommand.

.. code-block:: bash

   $ pwd
   /home/roppenheimer/waves-tutorials
   $ waves fetch --overwrite tutorials/tutorial_12_archival && cp tutorial_12_archival tutorial_task_reuse
   WAVES fetch
   Destination directory: '/home/roppenheimer/waves-tutorials'

**********
SConscript
**********

A ``diff`` against the ``tutorial_12_archival`` file from :ref:`tutorial_archival_waves` is included below to help identify the
changes made in this tutorial.

.. admonition:: waves-tutorials/tutorial_task_reuse

   .. literalinclude:: tutorials_tutorial_task_reuse
      :language: Python
      :diff: tutorials_tutorial_12_archival

5. Create a new file named ``rectangle_geometry_partition.scons`` from the contents below

.. admonition:: waves-tutorials/rectangle_geometry_partition.scons

   .. literalinclude:: tutorials_rectangle_geometry_partition.scons
      :language: Python
      :lineno-match:

6. Create a new file named ``rectangle_mesh_solverprep_solve_extract.scons`` from the contents below

.. admonition:: waves-tutorials/rectangle_mesh_solverprep_solve_extract.scons

   .. literalinclude:: tutorials_rectangle_mesh_solverprep_solve_extract.scons
      :language: Python
      :lineno-match:

**********
SConstruct
**********

A ``diff`` against the ``SConstruct`` file from :ref:`tutorial_archival_waves` is included below to help identify the
changes made in this tutorial.

.. admonition:: waves-tutorials/SConstruct

   .. literalinclude:: tutorials_tutorial_task_reuse_SConstruct
      :language: Python
      :diff: tutorials_tutorial_12_archival_SConstruct

*************
Build Targets
*************

7. Build the new targets

.. code-block:: bash

   $ pwd
   /home/roppenheimer/waves-tutorials
   $ scons tutorial_task_reuse --jobs=4

************
Output Files
************

.. code-block:: bash

   $ pwd
   /home/roppenheimer/waves-tutorials
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
   |-- rectangle_compression.inp
   |-- rectangle_compression.inp.in
   |-- rectangle_compression_DATACHECK.023
   |-- rectangle_compression_DATACHECK.abaqus_v6.env
   |-- rectangle_compression_DATACHECK.com
   |-- rectangle_compression_DATACHECK.dat
   |-- rectangle_compression_DATACHECK.mdl
   |-- rectangle_compression_DATACHECK.msg
   |-- rectangle_compression_DATACHECK.odb
   |-- rectangle_compression_DATACHECK.prt
   |-- rectangle_compression_DATACHECK.sim
   |-- rectangle_compression_DATACHECK.stdout
   |-- rectangle_compression_DATACHECK.stt
   |-- rectangle_geometry.abaqus_v6.env
   |-- rectangle_geometry.cae
   |-- rectangle_geometry.jnl
   |-- rectangle_geometry.stdout
   |-- rectangle_mesh.abaqus_v6.env
   |-- rectangle_mesh.cae
   |-- rectangle_mesh.inp
   |-- rectangle_mesh.jnl
   |-- rectangle_mesh.stdout
   |-- rectangle_partition.abaqus_v6.env
   |-- rectangle_partition.cae
   |-- rectangle_partition.jnl
   `-- rectangle_partition.stdout

   0 directories, 35 files
