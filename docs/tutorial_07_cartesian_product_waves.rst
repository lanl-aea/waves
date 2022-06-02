.. _tutorial_cartesian_product_waves:

##########################
Tutorial 07: Include Files
##########################

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

3. Create a directory ``tutorial_07_cartesian_product`` in the ``waves-eabm-tutorial`` directory.

.. code-block:: bash

   $ pwd
   /path/to/waves-eabm-tutorial
   $ mkdir tutorial_07_cartesian_product

4. Copy the ``tutorial_06_include_files/SConscript`` file into the newly created ``tutorial_07_cartesian_product``
   directory.

.. code-block:: bash

   $ pwd
   /path/to/waves-eabm-tutorial
   $ cp tutorial_06_include_files/SConscript tutorial_07_cartesian_product/

**********
SConscript
**********

A ``diff`` against the ``SConscript`` file from :ref:`tutorial_simulation_waves` is included below to help identify the
changes made in this tutorial.

.. admonition:: waves-eabm-tutorial/tutorial_07_cartesian_product/SConscript

   .. literalinclude:: tutorial_07_cartesian_product_SConscript
      :language: Python
      :diff: tutorial_06_include_files_SConscript

**********
SConstruct
**********

A ``diff`` against the ``SConstruct`` file from :ref:`tutorial_simulation_waves` is included below to help identify the
changes made in this tutorial.

.. admonition:: waves-eabm-tutorial/SConstruct

   .. literalinclude:: eabm_tutorial_07_cartesian_product_SConstruct
      :language: Python
      :diff: eabm_tutorial_06_include_files_SConstruct

*************
Build Targets 
*************

5. Build the new targets

.. code-block:: bash

   $ pwd
   /path/to/waves-eabm-tutorial
   $ scons tutorial_07_cartesian_product

************
Output Files
************
