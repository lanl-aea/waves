.. _tutorial_sobol_sequence_waves:

###########################
Tutorial 07: Sobol Sequence
###########################

.. include:: wip_warning.txt

**********
References
**********

* |PROJECT| :ref:`parameter_generator_api` API: :meth:`waves.parameter_generators.SobolSequence`
* `Xarray`_ and the `xarray dataset`_ :cite:`xarray,hoyer2017xarray`

***********
Environment
***********

.. include:: tutorial_environment_activation.txt

*******************
Directory Structure
*******************

3. Copy the ``tutorial_07_cartesian_product`` file to a new file named ``tutorial_07_sobol_sequence``

.. code-block:: bash

   $ pwd
   /path/to/waves-tutorials
   $ cp tutorial_07_cartesian_product tutorial_07_sobol_sequence

********************
Parameter Study File
********************

4. Create a new file ``eabm_package/python/single_element_compression_sobol_sequence.py`` from the content below.

.. admonition:: waves-tutorials/eabm_package/python/single_element_compression_sobol_sequence.py

   .. literalinclude:: python_single_element_compression_sobol_sequence.py
      :language: Python

**********
SConscript
**********

A ``diff`` against the ``SConscript`` file from :ref:`tutorial_cartesian_product_waves` is included below to help identify the
differences between the two parameter generators.

.. admonition:: waves-tutorials/tutorial_07_sobol_sequence

   .. literalinclude:: tutorials_tutorial_07_sobol_sequence
      :language: Python
      :diff: tutorials_tutorial_07_cartesian_product

**********
SConstruct
**********

A ``diff`` against the ``SConstruct`` file from :ref:`tutorial_cartesian_product_waves` is included below to help identify the
changes made in this tutorial.

.. admonition:: waves-tutorials/SConstruct

   .. literalinclude:: tutorials_tutorial_07_sobol_sequence_SConstruct
      :language: Python
      :diff: tutorials_tutorial_07_cartesian_product_SConstruct

*************
Build Targets
*************

5. Build the new targets

.. code-block:: bash

   $ pwd
   /path/to/waves-tutorials
   $ scons tutorial_07_sobol_sequence --jobs=4

************
Output Files
************

.. code-block:: bash

   $ pwd
   /path/to/waves-tutorials
   $ tree build/tutorial_07_sobol_sequence/parameter_set0/
   build/tutorial_07_sobol_sequence/parameter_set0/
   |-- abaqus.rpy
   |-- abaqus.rpy.1
   |-- abaqus.rpy.2
   |-- assembly.inp
   |-- boundary.inp
   |-- field_output.inp
   |-- history_output.inp
   |-- materials.inp
   |-- parts.inp
   |-- single_element_compression.abaqus_v6.env
   |-- single_element_compression.com
   |-- single_element_compression.dat
   |-- single_element_compression.inp
   |-- single_element_compression.inp.in
   |-- single_element_compression.msg
   |-- single_element_compression.odb
   |-- single_element_compression.prt
   |-- single_element_compression.sta
   |-- single_element_compression.stdout
   |-- single_element_geometry.abaqus_v6.env
   |-- single_element_geometry.cae
   |-- single_element_geometry.jnl
   |-- single_element_geometry.stdout
   |-- single_element_mesh.abaqus_v6.env
   |-- single_element_mesh.cae
   |-- single_element_mesh.inp
   |-- single_element_mesh.jnl
   |-- single_element_mesh.stdout
   |-- single_element_partition.abaqus_v6.env
   |-- single_element_partition.cae
   |-- single_element_partition.jnl
   `-- single_element_partition.stdout

   0 directories, 32 files
