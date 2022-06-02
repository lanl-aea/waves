.. _tutorial_parameter_substitution_waves:

###################################
Tutorial 05: Parameter Substitution
###################################

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

3. Create a directory ``tutorial_05_parameter_substitution`` in the ``model-eabm-tutorial`` directory.

.. code-block:: bash

   $ pwd
   /path/to/model-eabm-tutorial
   $ mkdir tutorial_05_parameter_substitution

4. Copy the ``tutorial_04_simulation/SConscript`` file into the newly created ``tutorial_05_parameter_substitution``
   directory.

.. code-block:: bash

   $ pwd
   /path/to/model-eabm-tutorial
   $ cp tutorial_04_simulation/SConscript tutorial_05_parameter_substitution/

**********
SConscript
**********

A ``diff`` against the ``SConscript`` file from :ref:`tutorial_simulation_waves` is included below to help identify the
changes made in this tutorial.

.. admonition:: waves-eabm-tutorial/tutorial_05_parameter_substitution/SConscript

   .. literalinclude:: tutorial_05_parameter_substitution_SConscript
      :language: Python
      :lineno-match:
      :diff: tutorial_04_simulation_SConscript

**********
SConstruct
**********

A ``diff`` against the ``SConstruct`` file from :ref:`tutorial_simulation_waves` is included below to help identify the
changes made in this tutorial.

.. admonition:: waves-eabm-tutorial/SConstruct

   .. literalinclude:: eabm_tutorial_05_parameter_substitution_SConstruct
      :language: Python
      :lineno-match:
      :diff: eabm_tutorial_04_simulation_SConstruct

*************
Build Targets 
*************

5. Build the new targets

.. code-block:: bash

   $ pwd
   /path/to/model-eabm-tutorial
   $ scons tutorial_05_parameter_substitution
