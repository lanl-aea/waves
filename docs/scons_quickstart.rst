.. _scons_quickstart:

################
SCons Quickstart
################

.. include:: scons_tutorial_introduction.txt

***********
Environment
***********

.. include:: scons_tutorial_environment.txt

*******************
Directory Structure
*******************

.. include:: scons_tutorial_directory.txt

***************
SConstruct File
***************

5. Create a file named ``scons_quickstart_SConstruct`` from the contents below.

.. admonition:: waves-tutorials/scons_quickstart_SConstruct

    .. literalinclude:: tutorials_scons_quickstart_SConstruct
       :language: Python
       :lineno-match:

****************
Building targets
****************

.. code-block::

   $ pwd
   /home/roppenheimer/waves-tutorials
   $ scons --sconstruct=scons_quickstart_SConstruct single_element

.. note::

   The ``--sconstruct`` option is required because the quickstart project configuration file name doesn't follow the
   `SCons`_ naming convention, ``SConstruct``.

************
Output Files
************

.. code-block:: bash

   $ pwd
   /home/roppenheimer/waves-tutorials
   $ tree build_scons_quickstart/
   build_scons_quickstart/
   |-- abaqus.rpy
   |-- abaqus.rpy.10
   |-- abaqus.rpy.7
   |-- abaqus.rpy.8
   |-- abaqus.rpy.9
   |-- assembly.inp
   |-- boundary.inp
   |-- field_output.inp
   |-- history_output.inp
   |-- materials.inp
   |-- parts.inp
   |-- single_element_compression.com
   |-- single_element_compression.dat
   |-- single_element_compression.inp
   |-- single_element_compression.msg
   |-- single_element_compression.odb
   |-- single_element_compression.prt
   |-- single_element_compression.sta
   |-- single_element_geometry.cae
   |-- single_element_geometry.jnl
   |-- single_element_mesh.cae
   |-- single_element_mesh.inp
   |-- single_element_mesh.jnl
   |-- single_element_partition.cae
   `-- single_element_partition.jnl

   0 directories, 25 files
