.. _quickstart:

##########
Quickstart
##########

This quickstart will create a minimal version of the full tutorial project definitions below using a single project
definition file. These tutorials and this quickstart describe the computational engineering workflow through simulation
execution. Using a single project definition requires `SCons`_ techniques that differ between the quickstart
``SConstruct`` file and the project defintion files, ``SConstruct`` and ``SConscript``, found in the full tutorials.

* :ref:`tutorialsconstruct`
* :ref:`tutorialgeometrywaves`
* :ref:`tutorial_partition_mesh_waves`
* :ref:`tutorial_solverprep_waves`
* :ref:`tutorial_simulation_waves`

***********
Environment
***********

.. include:: tutorial_environment_activation.txt

*******************
Directory Structure
*******************

3. Create the project directory structure and change to the project root directory with the following commands.

.. code-block:: bash

      $ mkdir -p ~/waves-eabm-tutorial
      $ cd ~/waves-eabm-tutorial
      $ pwd
      /home/roppenheimer/waves-eabm-tutorial

4. Download and copy the `WAVES-EABM abaqus source files`_ into the ``eabm_package/abaqus`` sub-directory. If you're on a
   linux system with `git`_ installed and read access on the `WAVES`_ repository, you can use `git archive`_ as below.

.. code-block:: bash

   $ pwd
   /home/roppenheimer/waves-eabm-tutorial
   $ git archive --format=zip --remote=ssh://git@re-git.lanl.gov:10022/kbrindley/waves.git HEAD:eabm/eabm_package/abaqus > source_abaqus.zip
   $ unzip source_abaqus.zip -d eabm_package/abaqus


***************
SConstruct File
***************

5. Create a file named ``SConstruct`` from the contents below.

.. admonition:: waves-eabm-tutorial/SConstruct

    .. literalinclude:: eabm_quickstart_SConstruct
       :language: Python
       :lineno-match:

****************
Building targets
****************

.. code-block::

   $ pwd
   /path/to/waves-eabm-tutorial
   $ scons single_element

************
Output Files
************

.. code-block:: bash

   $ pwd
   /path/to/waves-eabm-tutorial
   $ tree build_quickstart/
   build_quickstart/
   |-- abaqus.rpy
   |-- abaqus.rpy.1
   |-- abaqus.rpy.2
   |-- amplitudes.inp
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
   |-- single_element_compression.log
   |-- single_element_compression.msg
   |-- single_element_compression.odb
   |-- single_element_compression.prt
   |-- single_element_compression.sta
   |-- single_element_compression_DATACHECK.023
   |-- single_element_compression_DATACHECK.abaqus_v6.env
   |-- single_element_compression_DATACHECK.com
   |-- single_element_compression_DATACHECK.dat
   |-- single_element_compression_DATACHECK.log
   |-- single_element_compression_DATACHECK.mdl
   |-- single_element_compression_DATACHECK.msg
   |-- single_element_compression_DATACHECK.odb
   |-- single_element_compression_DATACHECK.prt
   |-- single_element_compression_DATACHECK.sim
   |-- single_element_compression_DATACHECK.stt
   |-- single_element_geometry.abaqus_v6.env
   |-- single_element_geometry.cae
   |-- single_element_geometry.jnl
   |-- single_element_geometry.log
   |-- single_element_mesh.abaqus_v6.env
   |-- single_element_mesh.cae
   |-- single_element_mesh.inp
   |-- single_element_mesh.jnl
   |-- single_element_mesh.log
   |-- single_element_partition.abaqus_v6.env
   |-- single_element_partition.cae
   |-- single_element_partition.jnl
   `-- single_element_partition.log

   0 directories, 43 files
