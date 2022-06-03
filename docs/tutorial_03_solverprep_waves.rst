.. _tutorial_solverprep_waves:

#######################
Tutorial 03: SolverPrep
#######################

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

3. Create a directory ``tutorial_03_solverprep`` in the ``waves-eabm-tutorial`` directory.

.. code-block:: bash

   $ pwd
   /path/to/waves-eabm-tutorial
   $ mkdir tutorial_03_solverprep

4. Copy the ``tutorial_02_partition_mesh/SConscript`` file into the newly created ``tutorial_03_solverprep``
   directory.

.. code-block:: bash

   $ pwd
   /path/to/waves-eabm-tutorial
   $ cp tutorial_02_partition_mesh/SConscript tutorial_03_solverprep/

**********
SConscript
**********

.. admonition:: waves-eabm-tutorial/tutorial_03_solverprep/SConscript
    
    .. literalinclude:: tutorial_03_solverprep_SConscript
       :language: Python
       :lineno-match:
       :emphasize-lines: 5
       :end-before: marker-1

.. admonition:: waves-eabm-tutorial/tutorial_03_solverprep/SConscript

    .. literalinclude:: tutorial_03_solverprep_SConscript
       :language: Python
       :lineno-match:
       :start-after: marker-2
       :end-before: marker-3


A ``diff`` against the ``SConscript`` file from :ref:`tutorial_partition_mesh_waves` is included below to help identify the
changes made in this tutorial.

.. admonition:: waves-eabm-tutorial/tutorial_03_solverprep/SConscript

   .. literalinclude:: tutorial_03_solverprep_SConscript
      :language: Python
      :diff: tutorial_02_partition_mesh_SConscript

******************
Solver Input Files
******************

4. Download and copy the `WAVES-EABM abaqus source files`_ into your existing ``source/abaqus`` 
   sub-directory. If you're on a linux system with `git`_ installed and read access on the 
   `WAVES`_ repository, you can use `git archive`_ as below.

.. note::
    
    The commands in the code block below are intended for the user to copy and paste into 
    their bash shell. These commands utilize the concepts of `Bash Variables`_, `Bash 
    Arrays`_ and `Bash Parameter Expansion`_.

.. code-block:: bash

   $ pwd
   /home/roppenheimer/waves-eabm-tutorial
   $ file_list=("single_element_compression" "amplitudes" "boundary" "field_output" "materials" "parts" "history_output")
   $ file_list=("${file_list[@]/%/.inp}")
   $ repo_ssh="ssh://git@re-git.lanl.gov:10022/kbrindley/waves.git"
   $ git archive --format=zip --remote=$repo_ssh HEAD:eabm/source/abaqus ${file_list[*]} > source_abaqus.zip
   $ unzip source_abaqus.zip -d source/abaqus

**********
SConstruct
**********

A ``diff`` against the ``SConstruct`` file from :ref:`tutorial_partition_mesh_waves` is included below to help identify the
changes made in this tutorial.

.. admonition:: waves-eabm-tutorial/SConstruct

   .. literalinclude:: eabm_tutorial_03_solverprep_SConstruct
      :language: Python
      :diff: eabm_tutorial_02_partition_mesh_SConstruct

*************
Build Targets 
*************

5. Build the new targets

.. code-block:: bash

   $ pwd
   /path/to/waves-eabm-tutorial
   $ scons tutorial_03_solverprep

************
Output Files
************

Explore the contents of the ``build`` directory using the ``tree`` command against the
``build`` directory, as shown below.

.. code-block:: bash

    $ pwd
    /home/roppenheimer/waves-eabm-tutorial
    build/
    ├── tutorial_01_geometry
    │   ├── abaqus.rpy
    │   ├── single_element_geometry.abaqus_v6.env
    │   ├── single_element_geometry.cae
    │   ├── single_element_geometry.jnl
    │   └── single_element_geometry.log
    ├── tutorial_02_partition_mesh
    │   ├── abaqus.rpy
    │   ├── abaqus.rpy.1
    │   ├── abaqus.rpy.2
    │   ├── single_element_geometry.abaqus_v6.env
    │   ├── single_element_geometry.cae
    │   ├── single_element_geometry.jnl
    │   ├── single_element_geometry.log
    │   ├── single_element_mesh.abaqus_v6.env
    │   ├── single_element_mesh.cae
    │   ├── single_element_mesh.inp
    │   ├── single_element_mesh.jnl
    │   ├── single_element_mesh.log
    │   ├── single_element_partition.abaqus_v6.env
    │   ├── single_element_partition.cae
    │   ├── single_element_partition.jnl
    │   └── single_element_partition.log
    └── tutorial_03_solverprep
        ├── abaqus.rpy
        ├── abaqus.rpy.1
        ├── abaqus.rpy.2
        ├── amplitudes.inp
        ├── assembly.inp
        ├── boundary.inp
        ├── field_output.inp
        ├── history_output.inp
        ├── materials.inp
        ├── parts.inp
        ├── single_element_compression.inp
        ├── single_element_geometry.abaqus_v6.env
        ├── single_element_geometry.cae
        ├── single_element_geometry.jnl
        ├── single_element_geometry.log
        ├── single_element_mesh.abaqus_v6.env
        ├── single_element_mesh.cae
        ├── single_element_mesh.inp
        ├── single_element_mesh.jnl
        ├── single_element_mesh.log
        ├── single_element_partition.abaqus_v6.env
        ├── single_element_partition.cae
        ├── single_element_partition.jnl
        └── single_element_partition.log
    
    3 directories, 45 files

Inside the build directory are three sub-directories. ``tutorial_01_geometry`` and 
``tutorial_02_partition_mesh``  remain from the previous two tutorials. The third 
directory, ``tutorial_03_solverprep``, pertains to the targets we just build. 


