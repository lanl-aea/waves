.. _waves_quickstart:

######################
SCons-WAVES Quickstart
######################

This quickstart will create a minimal, single file project configuration matching the tutorial listed below.

* :ref:`tutorialsconstruct`
* :ref:`tutorial_geometry_waves`
* :ref:`tutorial_partition_mesh_waves`
* :ref:`tutorial_solverprep_waves`
* :ref:`tutorial_simulation_waves`

These tutorials and this quickstart describe the computational engineering workflow through simulation execution. Using
a single project configuration file requires `SCons`_ techniques that differ between the quickstart ``SConstruct`` file and
the project configuration files, ``SConstruct`` and ``SConscript``, found in the full tutorials. Consequently, this
quickstart will use a separate name for the project configuration file, ``waves_quickstart_SConstruct``, to allow the
tutorials and this quickstart to share a common tutorial directory.

***********
Environment
***********

.. include:: tutorial_environment_activation.txt

*******************
Directory Structure
*******************

.. include:: scons_tutorial_directory.txt

***************
SConstruct File
***************

5. Create a file named ``waves_quickstart_SConstruct`` from the contents below.

.. admonition:: waves-tutorials/waves_quickstart_SConstruct

    .. literalinclude:: tutorials_waves_quickstart_SConstruct
       :language: Python
       :lineno-match:

****************
Building targets
****************

.. code-block::

   $ pwd
   /home/roppenheimer/waves-tutorials
   $ scons --sconstruct=waves_quickstart_SConstruct rectangle

.. note::

   The ``--sconstruct`` option is required because the quickstart project configuration file name doesn't follow the
   `SCons`_ naming convention, ``SConstruct``.

************
Output Files
************

.. code-block:: bash

   $ pwd
   /home/roppenheimer/waves-tutorials
   $ tree build_waves_quickstart/
   build_waves_quickstart/
   ├── abaqus.rpy
   ├── abaqus.rpy.1
   ├── abaqus.rpy.2
   ├── assembly.inp
   ├── boundary.inp
   ├── field_output.inp
   ├── history_output.inp
   ├── materials.inp
   ├── parts.inp
   ├── rectangle_compression.abaqus_v6.env
   ├── rectangle_compression.com
   ├── rectangle_compression.dat
   ├── rectangle_compression.inp
   ├── rectangle_compression.msg
   ├── rectangle_compression.odb
   ├── rectangle_compression.prt
   ├── rectangle_compression.sta
   ├── rectangle_compression.stdout
   ├── rectangle_geometry.abaqus_v6.env
   ├── rectangle_geometry.cae
   ├── rectangle_geometry.jnl
   ├── rectangle_geometry.stdout
   ├── rectangle_mesh.abaqus_v6.env
   ├── rectangle_mesh.cae
   ├── rectangle_mesh.inp
   ├── rectangle_mesh.jnl
   ├── rectangle_mesh.stdout
   ├── rectangle_partition.abaqus_v6.env
   ├── rectangle_partition.cae
   ├── rectangle_partition.jnl
   └── rectangle_partition.stdout

   0 directories, 31 files

**********************
Workflow Visualization
**********************

.. code-block::

   $ pwd
   /home/roppenheimer/waves-tutorials
   $ waves visualize --sconstruct waves_quickstart_SConstruct rectangle --output-file waves_quickstart.png --width=28 --height=5 --exclude-list .stdout .jnl .env /usr/bin

.. figure:: waves_quickstart.png
   :align: center
