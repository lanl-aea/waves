.. _tutorial_partition_mesh_waves:

###############################
Tutorial 02: Partition and Mesh
###############################

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

3. Create a directory ``tutorial_02_partition_mesh`` in the ``waves-eabm-turorial`` directory.

.. code-block:: bash
   
   $ pwd
   /path/to/waves-eabm-tutorial
   $ mkdir tutorial_05_parameter_substitution

4. Copy the ``tutorial_01_geometry/SConscript`` file into the newly created ``tutorial_02_partition_mesh`` directory.

.. code-block:: bash
   
   $ pwd
   /path/to/waves-eabm-tutorial
   $ cp tutorial_01_geometry/SConscript tutorial_02_partition_mesh/

**********
SConscript
**********

5. Modify your ``tutorial_02_partition_mesh/SConscript`` file
A ``diff`` against the ``SConscript`` file from :ref:`tutorial_geometry_waves` is included below to help identify the 
changes made in this tutorial.

.. admonition:: waves-eabm-tutorial/tutorial_02_partition_mesh/SConscript
   
   .. literalinclude:: tutorial_02_partition_mesh_SConscript
      :language: Python
      :diff: tutorial_01_geometry_SConscript

*******************
Abaqus Journal File
*******************

.. admonition:: single_element_partition.py
   
    .. literalinclude:: abaqus_single_element_partition.py
        :language: Python
        :lineno-match:

.. admonition:: single_element_mesh.py
   
    .. literalinclude:: abaqus_single_element_mesh.py
        :language: Python
        :lineno-match:

**********
SConstruct
**********

A ``diff`` against the SConstruct file from :ref:`tutorial_geometry_waves` is included below to help identify the 
changes made in this tutorial.

   ..  admonition:: waves-eabm-tutorial/SConstruct

     .. literalinclude:: eabm_tutorial_02_partition_mesh_SConstruct
        :language: python
        :diff: eabm_tutorial_01_geometry_SConstruct

*************
Build Targets
*************

5. Build the new targets

.. code-block:: bash
   
   $ pwd
   /path/to/waves-eabm-tutorial
   $ scons tutorial_02_partition_mesh

************
Output Files
************
