.. _scons_quickstart:

################
SCons Quickstart
################

.. note::

   Unlike the :ref:`waves_quickstart`, this tutorial will use native `SCons`_ code without the `WAVES`_ extensions and
   builders. This tutorial is included as an example for using native `SCons`_ techniques when `WAVES`_ does not support
   required third-party software, such as numeric solvers, or for when a modsim project requires unique builder behavior.

This quickstart will create a pure `SCons`_, minimal, single file project definition matching the tutorials listed below.

* :ref:`tutorialsconstruct`
* :ref:`tutorial_geometry_waves`
* :ref:`tutorial_partition_mesh_waves`
* :ref:`tutorial_solverprep_waves`
* :ref:`tutorial_simulation_waves`

These tutorials and this quickstart describe the computational engineering workflow through simulation execution. Using
a single project definition file requires `SCons`_ techniques that differ between the quickstart ``SConstruct`` file and
the project definition files, ``SConstruct`` and ``SConscript``, found in the full tutorials. Consequently, this
quickstart will use a separate name for the project definition file, ``scons_quickstart_SConstruct``, to allow the
tutorials and this quickstart to share a common tutorial directory.

***********
Environment
***********

`SCons`_ can be installed in a `Conda`_ environment with the `Conda`_ package manager. See the `Conda installation`_ and
`Conda environment management`_ documentation for more details about using `Conda`_.

1. Create the environment if it doesn't exist

   .. code-block::

      $ conda create --name waves-eabm-env --channel conda-forge scons

2. Activate the environment

   .. code-block::

      $ conda activate waves-eabm-env

*******************
Directory Structure
*******************

3. Create the project directory structure and change to the project root directory with the following commands.

.. code-block:: bash

      $ mkdir -p ~/waves-eabm-tutorial/eabm_package/abaqus
      $ cd ~/waves-eabm-tutorial
      $ pwd
      /home/roppenheimer/waves-eabm-tutorial

4. Download and copy the `WAVES-EABM abaqus source files`_ into the ``eabm_package/abaqus`` sub-directory. If you're on a
   linux system with `git`_ installed and read access on the `WAVES`_ repository, you can use `git archive`_ as below.

.. code-block:: bash

   $ pwd
   /home/roppenheimer/waves-eabm-tutorial
   $ git archive --format=zip --remote=ssh://git@re-git.lanl.gov:10022/aea/python-projects/waves.git HEAD:eabm/eabm_package/abaqus > source_abaqus.zip
   $ unzip source_abaqus.zip -d eabm_package/abaqus


***************
SConstruct File
***************

5. Create a file named ``scons_quickstart_SConstruct`` from the contents below.

.. admonition:: waves-eabm-tutorial/scons_quickstart_SConstruct

    .. literalinclude:: eabm_scons_quickstart_SConstruct
       :language: Python
       :lineno-match:

****************
Building targets
****************

.. code-block::

   $ pwd
   /home/roppenheimer/waves-eabm-tutorial
   $ scons --sconstruct=scons_quickstart_SConstruct single_element

.. note::

   The ``--sconstruct`` option is required because the quickstart project definition file name doesn't follow the
   `SCons`_ naming convention, ``SConstruct``.

************
Output Files
************

.. code-block:: bash

   $ pwd
   /home/roppenheimer/waves-eabm-tutorial
   $ tree build_scons_quickstart/
   build_scons_quickstart/
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
   |-- single_element_compression.com
   |-- single_element_compression.dat
   |-- single_element_compression.inp
   |-- single_element_compression.msg
   |-- single_element_compression.odb
   |-- single_element_compression.prt
   |-- single_element_compression.sta
   |-- single_element_compression_DATACHECK.023
   |-- single_element_compression_DATACHECK.com
   |-- single_element_compression_DATACHECK.dat
   |-- single_element_compression_DATACHECK.mdl
   |-- single_element_compression_DATACHECK.msg
   |-- single_element_compression_DATACHECK.odb
   |-- single_element_compression_DATACHECK.prt
   |-- single_element_compression_DATACHECK.sim
   |-- single_element_compression_DATACHECK.stt
   |-- single_element_geometry.cae
   |-- single_element_geometry.jnl
   |-- single_element_mesh.cae
   |-- single_element_mesh.inp
   |-- single_element_mesh.jnl
   |-- single_element_partition.cae
   `-- single_element_partition.jnl
   
   0 directories, 33 files
