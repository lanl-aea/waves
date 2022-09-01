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

This parameter study will define a mesh convergence study where the global size of the finite elements in the model 
decreased several times by a factor of two.

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

.. admonition:: waves-eabm-tutorial/tutorial_mesh_convergence/SConscript
   
   .. literalinclude:: tutorial_mesh_convergence_SConscript
      :language: Python
      :lineno-match:
      :end-before: marker-2
      :emphasize-lines: 7, 27-31

The highlighted code above points out two key changes from ``diff`` at the beginning of the file. First, we import the 
parameter_schema from the ``single_element_compression_mesh_convergence.py`` file you created in the beginning of this 
tutorial. The second change is the addition of a ``simulation_constants`` dictionary. This parameter study only changes 
the meshing ``global_seed`` parameter, and all other model parameters stay constant. One way to achieve this would be to 
set the remaining parameters as single-value parameter sets in the ``parameter_schema``. This was done with the 
``global_seed`` and ``displacement`` parameters in :ref:`tutorial_cartesian_product_waves`. Rather, we will set the 
``width``, ``height``, and ``displacement`` variables as constants in the ``SConscript`` file, and they will not appear 
in our parameter study definition. The ``parameter_schema`` and ``simulaiton_constants`` dictionaries will be combined 
later in the ``SConscript`` file.


      

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
