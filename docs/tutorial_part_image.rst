.. _tutorial_part_image:

####################
Tutorial: Part Image
####################

This is an example implementation where an Abaqus Python script is used to export an assembly view image of an Abaqus
model from an input or CAE file.

**********
References
**********

Below is a list of references for more information about topics that are not explicitly
covered in this tutorial.

* `Abaqus Scripting`_ :cite:`ABAQUS`
* `Abaqus Python Environment`_ :cite:`ABAQUS`

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

4. Download and copy the ``tutorial_12_archival`` file to a new file named ``tutorial_part_image`` with the
   :ref:`waves_cli` :ref:`waves_fetch_cli` subcommand.

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
   contents below which contains the ``main()`` function.

.. admonition:: waves-tutorials/modsim_package/abaqus/export_abaqus_image.py

   .. literalinclude:: abaqus_export_abaqus_image.py
      :language: Python
      :lineno-match:
      :end-before: marker-1

The ``export_abaqus_image.py`` file is an Abaqus journal file. The top of the file imports standard library modules,
Abaqus modules, and the ``abaqus_utilities.py`` module create in :ref:`tutorial_partition_mesh`. The ``main()`` function
takes two required arguments: ``input_file`` which is an Abaqus CAE ``*.cae`` or Abaqus input ``*.inp`` file and
``output_file`` which is the file path of the assembly view image that this function will create.

6. In the ``waves-tutorials/modsim_package/abaqus`` directory, continue editing the file ``export_abaqus_image.py``
   using the contents below which contains the rest of the script.

.. admonition:: waves-tutorials/modsim_package/abaqus/export_abaqus_image.py

   .. literalinclude:: abaqus_export_abaqus_image.py
      :language: Python
      :lineno-match:
      :start-after: marker-1

The ``image()`` function utilizes the rest of the optional arguments that were passed from the ``main()`` function. The
arguments ``color_map``, ``x_angle``, ``y_angle``, and ``z_angle`` are used to adjust the viewer window. The
``model_name`` and ``part_name`` are used to set the Abaqus part assembly. The ``image_size`` parameter can change the
size of your output image. All of these arguments are optional and have default values to rely on if no value was
specified.

**********
SConscript
**********

7. Add the ``images`` task list and alias to the ``tutorial_part_image`` SConscript file. A``diff`` against the
   ``tutorial_12_archival`` file from :ref:`tutorial_archival` is included below to help identify the changes made in
   this tutorial.

.. admonition:: waves-tutorials/tutorial_part_image

   .. literalinclude:: tutorials_tutorial_part_image
      :language: Python
      :diff: tutorials_tutorial_12_archival

Generating images will be part of a separate workflow. To do this we have created an ``images`` list that will capture
the `SCons`_ tasks and have mapped a new alias to that list.

**********
SConstruct
**********

8. Add the ``tutorial_part_image`` SConscript file to the workflow. A ``diff`` against the ``SConstruct`` file from
   :ref:`tutorial_archival` is included below to help identify the changes made in this tutorial.

.. admonition:: waves-tutorials/SConstruct

   .. literalinclude:: tutorials_tutorial_part_image_SConstruct
      :language: Python
      :diff: tutorials_tutorial_12_archival_SConstruct

*************
Build Targets
*************

9. Build the new targets

.. code-block:: bash

   $ pwd
   /home/roppenheimer/waves-tutorials
   $ scons tutorial_part_image_images --jobs=4

************
Output Files
************

10. View the output files. Notice that the output files from :ref:`tutorial_regression_testing` have been created with
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
   ├── rectangle_compression.png.stdout
   ├── rectangle_geometry.cae
   ├── rectangle_geometry.cae.stdout
   ├── rectangle_geometry.jnl
   ├── rectangle_mesh.cae
   ├── rectangle_mesh.inp
   ├── rectangle_mesh.inp.stdout
   ├── rectangle_mesh.jnl
   ├── rectangle_partition.cae
   ├── rectangle_partition.cae.stdout
   └── rectangle_partition.jnl

   0 directories, 26 files
