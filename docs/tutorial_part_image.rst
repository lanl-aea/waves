.. _tutorial_part_image:

####################
Tutorial: Part Image
####################

This tutorial demonstrates one solution to re-using task definitions in multiple workflows. While the solution can be
implemented with per-task granularity, the task definitions in this tutorial are split into blocks to suite the
parameterization workflows of :ref:`tutorial_cartesian_product` and :ref:`tutorial_mesh_convergence`.

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
        $ waves fetch --overwrite --tutorial 12 && mv tutorial_12_archival_SConstruct SConstruct
        WAVES fetch
        Destination directory: '/home/roppenheimer/waves-tutorials'

4. Download and copy the ``tutorial_12_archival`` file to a new file named ``tutorial_part_image``
   with the :ref:`waves_cli` :ref:`waves_fetch_cli` subcommand.

.. code-block:: bash

   $ pwd
   /home/roppenheimer/waves-tutorials
   $ waves fetch --overwrite tutorials/tutorial_12_archival && cp tutorial_12_archival tutorial_part_image
   WAVES fetch
   Destination directory: '/home/roppenheimer/waves-tutorials'

*****************
Part-Image script
*****************

5. In the ``waves-tutorials/modsim_package/abaqus`` directory, create a file called ``export_abaqus_image.py`` using the
   contents below.

.. admonition:: waves-tutorials/modsim_package/abaqus/export_abaqus_image.py

   .. literalinclude:: abaqus_export_abaqus_image.py
      :language: Python

The post-processing script is the first Python 3 script introduced in the core tutorials. It differs from the Abaqus
journal files by executing against the Python 3 interpretter of the launching `Conda`_ environment where |PROJECT| is
installed. Unlike the Abaqus Python 2 environment used to execute journal files, users have direct control over this
environment and can use the full range of Python packages available with the `Conda`_ package manager.

**********
SConscript
**********

A ``diff`` against the ``tutorial_12_archival`` file from :ref:`tutorial_archival` is included below to help identify the
changes made in this tutorial.

.. admonition:: waves-tutorials/tutorial_part_image

   .. literalinclude:: tutorials_tutorial_part_image
      :language: Python
      :diff: tutorials_tutorial_12_archival

**********
SConstruct
**********

A ``diff`` against the ``SConstruct`` file from :ref:`tutorial_archival` is included below to help identify the
changes made in this tutorial.

.. admonition:: waves-tutorials/SConstruct

   .. literalinclude:: tutorials_tutorial_part_image_SConstruct
      :language: Python
      :diff: tutorials_tutorial_12_archival_SConstruct

*************
Build Targets
*************

7. Build the new targets

.. code-block:: bash

   $ pwd
   /home/roppenheimer/waves-tutorials
   $ scons tutorial_part_image --jobs=4

************
Output Files
************

.. code-block:: bash

   $ pwd
   /home/roppenheimer/waves-tutorials
   $ tree build/tutorial_part_image/parameter_set0/
   build/tutorial_part_image/parameter_set0/
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
