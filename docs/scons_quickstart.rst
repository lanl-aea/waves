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

3. Create the project directory structure and copy the `SCons quickstart source files`_ into the ``~/scons_quickstart``
   sub-directory with the :ref:`waves_cli` :ref:`waves_fetch_cli` subcommand.

.. code-block:: bash

      $ waves fetch tutorials/scons_quickstart --destination ~/scons_quickstart
      WAVES fetch
      Destination directory: '/home/roppenheimer/scons_quickstart'
      $ cd ~/scons_quickstart
      $ pwd
      /home/roppenheimer/scons_quickstart

***************
SConscript File
***************

For this quickstart, we will not discuss the main SCons configuration file named SConstruct, which contains project
setup boilerplate. :ref:`tutorialsconstruct` has a more complete discussion about the contents of the
``SConstruct`` file.

The ``SConscript`` file below contains the workflow task definitions. Review the source and target
files defining the workflow tasks. As discussed in :ref:`build_system`, a task definition also requires an action.

.. admonition:: scons_quickstart/SConscript

    .. literalinclude:: scons_quickstart_SConscript
       :language: Python
       :lineno-match:


****************
Building targets
****************

.. code-block::

   $ pwd
   /home/roppenheimer/scons_quickstart
   $ scons rectangle

************
Output Files
************

.. code-block:: bash

   $ pwd
   /home/roppenheimer/scons_quickstart
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

