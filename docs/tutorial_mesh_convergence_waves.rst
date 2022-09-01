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

6. A ``diff`` against the ``SConscript`` file from :ref:`tutorial_regression_testing_waves` is included below to help 
   identify the changes made in this tutorial. Use the diff to update your ``tutorial_10_regression_testing/SConscript`` 
   file, and then follow along in paragraphs that follow to understand the meaning of these changes.

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
in our parameter study definition. The individual parameters from the ``parameter_schema`` and ``simulaiton_constants`` 
dictionaries will be combined later in the ``SConscript`` file.

.. admonition:: waves-eabm-tutorial/tutorial_mesh_convergence/SConscript

   .. literalinclude:: tutorial_mesh_convergence_SConscript
      :language: Python
      :lineno-match:
      :start-after: marker-3
      :end-before: marker-4
      :emphasize-lines: 5-6, 14-15, 20-21, 26

The code above is largely copy and paste from :ref:`tutorial_regression_testing_waves`, with a few significant 
differences:

* The ``# Geometry`` and ``# Partition`` code has been move out of the parameter study's ``for`` loop. As the parameter 
  study only involves a meshing parameter, the Geometry and Partition workflow steps need only happen once. Then, the 
  mesh convergence parameter study can re-use a common target.
* Note the highlighted lines for the ``target`` definitions in the ``# Geometry`` and ``# Partition`` code. Since this 
  code is no longer inside of the ``for`` loop, the ``set_name`` directory has been dropped from the ``target`` 
  definitions. As the first bullet eluded to, the targets for ``# Geometry`` and ``# Partition`` will be built in the 
  overall build directory, ``build/tutorial_mesh_convergence``.
* The folling two highlighted lines are necessary for the parameterized ``# Mesh`` workflow steps to re-use a common 
  target. First, the SCons file object for the ``single_element_partition.cae`` file is extracted from the target list, 
  ``partition_target``. The absolute path to the ``single_element_partition.cae`` file in the build directory is 
  made available as a variable in the second highlighted line.
* The final highlighted line shows how the ``simulation_variables`` dictionary is constructed by combining the 
  ``simulation_constants`` and the ``global_seed`` parameters for every simulation.

.. admonition:: waves-eabm-tutorial/tutorial_mesh_convergence/SConscript

   .. literalinclude:: tutorial_mesh_convergence_SConscript
      :language: Python
      :lineno-match:
      :start-after: marker-4
      :end-before: marker-5
      :emphasize-lines: 4-5, 11

The first two highlighted lines above demonstrate the usage of ``--input-file`` and ``--output--file`` command line 
arguments for the ``single_element_mesh.py`` file. In previous tutorials, we have accepted the default values for input 
and output files. In this case, however, we must specify that a common input file is used, as we want to re-use the 
target from the Partition workflow that happened before the ``for`` loop. If we would have accepted the default input 
file name, ``SCons`` would try to find a source file in the ``build/parameter_set{0,1,2,3}`` directory. We avoid this 
issue by providing the absolute path to the ``single_element_partition.cae`` as the ``--input-file``.

The ``--output-file`` command line argument is specified in this case only for demonstration (the default value would 
actually work just fine). It is important to note that the ``--output-file`` name is **not** given as ``set_name / 
journal_file``. This is because the :meth:`waves.builders.abaqus_journal` builder's action first changes the build 
directory to the parent directory of the first specified target, then the journal file is executed. This behavior is 
explained further in the :meth:`waves.builders.abaqus_journal` API.

The final highlighted line in the code above demonstrates the usage of an ``SCons`` file object as a source. Rathern 
than pointing to the ``single_element_partition.cae`` file via absolute path, we can let ``SCons`` find the file for us 
in the build directory. This is achieve by simply pointing to the ``SCons`` file object that was created when we 
specified ``single_element_partition.cae`` as a target in the ``# Partition`` workflow.

.. admonition:: waves-eabm-tutorial/tutorial_mesh_convergence/SConscript

   .. literalinclude:: tutorial_mesh_convergence_SConscript
      :language: Python
      :lineno-match:
      :start-after: marker-6

**********
SConstruct
**********

7. A ``diff`` against the ``SConstruct`` file from :ref:`tutorial_regression_testing_waves` is included below to help 
   identify the changes made in this tutorial. Make these changes to your ``SConstruct`` file.

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
