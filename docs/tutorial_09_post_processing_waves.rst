.. _tutorial_post_processing_waves:

############################
Tutorial 09: Post-Processing
############################

.. warning::

   The post-processing techniques in this tutorial are a work-in-progress. They should generally work into the future,
   but WAVES may add new behavior to make concatenating results files with the parameter study definition easier. Be sure
   to check back in on this tutorial frequently or watch the :ref:`changelog` for updates!

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

3. Create a directory ``tutorial_09_post_processing`` in the ``waves-eabm-tutorial`` directory.

.. code-block:: bash

   $ pwd
   /path/to/waves-eabm-tutorial
   $ mkdir tutorial_09_post_processing

4. Copy the ``tutorial_08_data_extraction/SConscript`` file into the newly created ``tutorial_09_post_processing``
   directory.

.. code-block:: bash

   $ pwd
   /path/to/waves-eabm-tutorial
   $ cp tutorial_08_data_extraction/SConscript tutorial_09_post_processing/

**********
SConscript
**********

A ``diff`` against the ``SConscript`` file from :ref:`tutorial_include_files_waves` is included below to help identify the
changes made in this tutorial.

.. admonition:: waves-eabm-tutorial/tutorial_09_post_processing/SConscript

   .. literalinclude:: tutorial_09_post_processing_SConscript
      :language: Python
      :diff: tutorial_08_data_extraction_SConscript

**********************
Post-processing script
**********************

5. In the ``waves-eabm-tutorial/eabm_package/python`` directory, create a file called ``plot_scatter.py`` using the
   contents below.

.. note::

   Depending on the memory and disk resources available and the size of the simulation workflow results, modsim projects
   may need to review the `Xarray`_ documentation for resource management specific to the projects' use case.

.. admonition:: waves-eabm-tutorial/eabm_package/python/plot_scatter.py

   .. literalinclude:: python_plot_scatter.py
      :language: Python

The script API and CLI are included in the :ref:`sphinx_api`: :ref:`eabm_plot_scatter_api` and :ref:`sphinx_cli`:
:ref:`eabm_plot_scatter_cli`, respectively.

**********
SConstruct
**********

A ``diff`` against the ``SConstruct`` file from :ref:`tutorial_include_files_waves` is included below to help identify the
changes made in this tutorial.

.. admonition:: waves-eabm-tutorial/SConstruct

   .. literalinclude:: eabm_tutorial_09_post_processing_SConstruct
      :language: Python
      :diff: eabm_tutorial_08_data_extraction_SConstruct

*************
Build Targets
*************

6. Build the new targets

.. code-block:: bash

   $ pwd
   /path/to/waves-eabm-tutorial
   $ scons tutorial_09_post_processing --jobs=4

************
Output Files
************

7. Observe the catenated parameter results and paramter study dataset in the post-processing task's STDOUT file

.. code-block::

   $ cat build/tutorial_09_post-processing/stress_strain_comparison.stdout
   <xarray.Dataset>
   Dimensions:           (parameter_sets: 4, step: 1, time: 5, elements: 1,
                          LE values: 4, S values: 4, parameters: 4)
   Coordinates:
     * LE values         (LE values) object 'LE11' 'LE22' 'LE33' 'LE12'
     * S values          (S values) object 'S11' 'S22' 'S33' 'S12'
     * elements          (elements) int64 1
       integrationPoint  (elements) int64 2
     * step              (step) object 'Step-1'
     * time              (time) float64 0.0175 0.07094 0.2513 0.86 1.0
     * parameter_sets    (parameter_sets) <U14 'parameter_set0' ... 'parameter_s...
     * parameters        (parameters) object 'width' 'height' ... 'displacement'
   Data variables:
       LE                (parameter_sets, step, time, elements, LE values) float32 ...
       S                 (parameter_sets, step, time, elements, S values) float32 ...
       values            (parameter_sets, parameters) float64 ...
