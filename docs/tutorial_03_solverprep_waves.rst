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

A ``diff`` against the ``SConscript`` file from :ref:`tutorial_partition_mesh_waves` is included below to help identify the
changes made in this tutorial.

.. admonition:: waves-eabm-tutorial/tutorial_03_solverprep/SConscript

   .. literalinclude:: tutorial_03_solverprep_SConscript
      :language: Python
      :diff: tutorial_02_partition_mesh_SConscript

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
