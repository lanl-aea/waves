.. _tutorial_mesh_convergence_waves:

#########################
Tutorial Mesh Convergence
#########################

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

3. Create a directory ``tutorial_mesh_convergence`` in the ``waves-eabm-tutorial`` directory.

.. code-block:: bash

   $ pwd
   /path/to/waves-eabm-tutorial
   $ mkdir tutorial_mesh_convergence

4. Copy the ``tutorial_10_regression_testing/SConscript`` file into the newly created ``tutorial_mesh_convergence``
   directory.

.. code-block:: bash

   $ pwd
   /path/to/waves-eabm-tutorial
   $ cp tutorial_10_regression_testing/SConscript tutorial_mesh_convergence

**********
SConscript
**********

A ``diff`` against the ``SConscript`` file from :ref:`tutorial_regression_testing_waves` is included below to help identify the
changes made in this tutorial.

.. admonition:: waves-eabm-tutorial/tutorial_mesh_convergence/SConscript

   .. literalinclude:: tutorial_mesh_convergence_SConscript
      :language: Python
      :diff: tutorial_10_regression_testing_SConscript

**********
SConstruct
**********

A ``diff`` against the ``SConstruct`` file from :ref:`tutorial_regression_testing_waves` is included below to help identify the
changes made in this tutorial.

.. admonition:: waves-eabm-tutorial/SConstruct

   .. literalinclude:: eabm_tutorial_mesh_convergence_SConstruct
      :language: Python
      :diff: eabm_tutorial_10_regression_testing_SConstruct

*************
Build Targets
*************

5. Build the datacheck targets without executing the full simulation workflow

.. code-block:: bash

   $ pwd
   /path/to/waves-eabm-tutorial
   $ scons tutorial_mesh_convergence --jobs=4

************
Output Files
************
