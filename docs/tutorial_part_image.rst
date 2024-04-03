.. _tutorial_part_image:

####################
Tutorial: Part Image
####################

**********
References
**********

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
   $ scons tutorial_part_image_images --jobs=4

************
Output Files
************

8. View the output files. Notice that the output files from :ref:`tutorial_regression_testing` have been created with
   the addition of the ``.png`` output files.

.. code-block:: bash

   $ pwd
   /home/roppenheimer/waves-tutorials
   $ tree build/tutorial_part_image/parameter_set0/
   build/tutorial_part_image/parameter_set0/
   ├── abaqus1.rec
   ├── abaqus.rpy
   ├── abaqus.rpy.1
   ├── abaqus.rpy.2
   ├── abaqus.rpy.3
   ├── abaqus.rpy.4
   ├── assembly.inp
   ├── boundary.inp
   ├── field_output.inp
   ├── history_output.inp
   ├── materials.inp
   ├── parts.inp
   ├── rectangle_compression.inp
   ├── rectangle_compression.inp.in
   ├── rectangle_compression.png
   ├── rectangle_compression.png.abaqus_v6.env
   ├── rectangle_compression.png.stdout
   ├── rectangle_geometry.cae
   ├── rectangle_geometry.cae.abaqus_v6.env
   ├── rectangle_geometry.cae.stdout
   ├── rectangle_geometry.jnl
   ├── rectangle_mesh.cae
   ├── rectangle_mesh.inp
   ├── rectangle_mesh.inp.abaqus_v6.env
   ├── rectangle_mesh.inp.stdout
   ├── rectangle_mesh.jnl
   ├── rectangle_partition.cae
   ├── rectangle_partition.cae.abaqus_v6.env
   ├── rectangle_partition.cae.stdout
   └── rectangle_partition.jnl

   0 directories, 30 files
