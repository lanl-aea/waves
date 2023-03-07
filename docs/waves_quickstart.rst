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
   $ scons --sconstruct=waves_quickstart_SConstruct single_element

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
