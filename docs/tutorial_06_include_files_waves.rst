.. _tutorial_include_files_waves:

##########################
Tutorial 06: Include Files
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

3. Create a directory ``tutorial_06_include_files`` in the ``model-eabm-tutorial`` directory.

.. code-block:: bash

   $ pwd
   /path/to/model-eabm-tutorial
   $ mkdir tutorial_06_include_files

4. Copy the ``tutorial_05_parameter_substitution/SConscript`` file into the newly created ``tutorial_06_include_files``
   directory.

.. code-block:: bash

   $ pwd
   /path/to/model-eabm-tutorial
   $ cp tutorial_05_parameter_substitution/SConscript tutorial_06_include_files/

**********
SConscript
**********

A ``diff`` against the ``SConscript`` file from :ref:`tutorial_simulation_waves` is included below to help identify the
changes made in this tutorial.

.. admonition:: waves-eabm-tutorial/tutorial_06_include_files/SConscript

   .. literalinclude:: tutorial_06_include_files_SConscript
      :language: Python
      :diff: tutorial_05_parameter_substitution_SConscript

**********
SConstruct
**********

A ``diff`` against the ``SConstruct`` file from :ref:`tutorial_simulation_waves` is included below to help identify the
changes made in this tutorial.

.. admonition:: waves-eabm-tutorial/SConstruct

   .. literalinclude:: eabm_tutorial_06_include_files_SConstruct
      :language: Python
      :diff: eabm_tutorial_05_parameter_substitution_SConstruct

*************
Build Targets 
*************

5. Build the new targets

.. code-block:: bash

   $ pwd
   /path/to/model-eabm-tutorial
   $ scons tutorial_06_include_files

************
Output Files
************
