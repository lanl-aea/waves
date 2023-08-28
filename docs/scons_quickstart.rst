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
   $ scons --sconstruct=scons_quickstart_SConstruct rectangle

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
   ├── abaqus.rpy
   ├── abaqus.rpy.1
   ├── abaqus.rpy.2
   ├── assembly.inp
   ├── boundary.inp
   ├── field_output.inp
   ├── history_output.inp
   ├── materials.inp
   ├── parts.inp
   ├── rectangle_compression.com
   ├── rectangle_compression.dat
   ├── rectangle_compression.inp
   ├── rectangle_compression.msg
   ├── rectangle_compression.odb
   ├── rectangle_compression.prt
   ├── rectangle_compression.sta
   ├── rectangle_geometry.cae
   ├── rectangle_geometry.jnl
   ├── rectangle_mesh.cae
   ├── rectangle_mesh.inp
   ├── rectangle_mesh.jnl
   ├── rectangle_partition.cae
   └── rectangle_partition.jnl

   0 directories, 23 files

