.. _waves_quickstart:

################
WAVES Quickstart
################

This quickstart will create a minimal, two file project configuration matching the tutorial listed below.

* :ref:`tutorialsconstruct`
* :ref:`tutorial_geometry_waves`
* :ref:`tutorial_partition_mesh_waves`
* :ref:`tutorial_solverprep_waves`
* :ref:`tutorial_simulation_waves`

These tutorials and this quickstart describe the computational engineering workflow through simulation execution. This
tutorial will use a different working directory than the rest of the core tutorials as both sets of tutorials contain files
with identical names.

***********
Environment
***********

.. include:: tutorial_environment_activation.txt

.. include:: version_check_warning.txt

*******************
Directory Structure
*******************

3. Create the project directory structure and copy the `WAVES quickstart source files`_ into the ``~/waves_quickstart``
   sub-directory with the :ref:`waves_cli` :ref:`waves_fetch_cli` subcommand.

.. code-block:: bash

      $ waves fetch tutorials/waves_quickstart --destination ~/waves_quickstart
      WAVES fetch
      Destination directory: '/home/roppenheimer/waves_quickstart'
      $ cd ~/waves_quickstart
      $ pwd
      /home/roppenheimer/waves_quickstart

***************
SConscript File
***************

For this quickstart, we will not discuss the main SCons configuration file named SConstruct, which contains project
setup boilerplate. :ref:`tutorialsconstruct` has a more complete discussion about the contents of the
``SConstruct`` file.

The ``SConscript`` file below contains the workflow task definitions. Review the source and target
files defining the workflow tasks. As discussed in :ref:`build_system`, a task definition also requires an action.
For convenience, WAVES provides builders for common engineering software with pre-defined task actions.
See the :meth:`waves.scons_extensions.abaqus_journal` and :meth:`waves.scons_extensions.abaqus_solver` for more
complete descriptions of the builder actions.

.. admonition:: waves_quickstart/SConscript

    .. literalinclude:: waves_quickstart_SConscript
       :language: Python
       :lineno-match:

****************
Building targets
****************

.. code-block::

   $ pwd
   /home/roppenheimer/waves_quickstart
   $ scons rectangle

************
Output Files
************

.. code-block:: bash

   $ pwd
   /home/roppenheimer/waves_quickstart
   $ tree build/
   build
   ├── abaqus_journal_utilities.py
   ├── abaqus_journal_utilities.pyc
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
   ├── rectangle_geometry.py
   ├── rectangle_geometry.stdout
   ├── rectangle_mesh.abaqus_v6.env
   ├── rectangle_mesh.cae
   ├── rectangle_mesh.inp
   ├── rectangle_mesh.jnl
   ├── rectangle_mesh.py
   ├── rectangle_mesh.stdout
   ├── rectangle_partition.abaqus_v6.env
   ├── rectangle_partition.cae
   ├── rectangle_partition.jnl
   ├── rectangle_partition.py
   ├── rectangle_partition.stdout
   └── SConscript

   0 directories, 37 files

**********************
Workflow Visualization
**********************

.. code-block::

   $ pwd
   /home/roppenheimer/waves_quickstart
   $ waves visualize rectangle --output-file waves_quickstart.png

.. figure:: waves_quickstart.png
   :align: center

