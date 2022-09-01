.. _tutorial_mesh_convergence_waves:

#########################
Tutorial Mesh Convergence
#########################

This tutorial is intended to demonstrate several key advanced usage features that were glossed over in previous 
tutorials. Specifically, this tutorial will discuss

* Building a parameter study from somewhere in the middle of the SCons workflow using a common target
* Utilizing journal file ``--input-file`` and ``--output-file`` arguments
* Using the ``plot_scatter.py`` script to create multiple plots

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

********************
Parameter Study File
********************

5. Create a new file ``eabm_package/python/single_element_compression_mesh_convergence.py`` from the content below.

.. admonition:: waves-eabm-tutorial/eabm_package/python/single_element_compression_mesh_convergence.py

   .. literalinclude:: python_single_element_compression_mesh_convergence.py
      :language: Python

**********
SConscript
**********

A ``diff`` against the ``SConscript`` file from :ref:`tutorial_regression_testing_waves` is included below to help identify the
changes made in this tutorial. Use the diff to update your ``tutorial_10_regression_testing/SConscript`` file, and then 
follow along in paragraphs that follow to understand the meaning of these changes.

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
