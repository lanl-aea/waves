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

* |PROJECT| :ref:`waves_builders_api` API: :meth:`waves.builders.python_script`
* |PROJECT| :ref:`parameter_generator_api` API: :meth:`waves.parameter_generators.CartesianProduct`
* `Xarray`_ and the `xarray dataset`_ :cite:`xarray,hoyer2017xarray`

***********
Environment
***********

.. include:: tutorial_environment_activation.txt

*******************
Directory Structure
*******************

3. Copy the ``tutorial_08_data_extraction`` file to a new file named ``tutorial_09_post_processing``

.. code-block:: bash

   $ pwd
   /path/to/waves-eabm-tutorial
   $ cp tutorial_08_data_extraction tutorial_09_post_processing

**********
SConscript
**********

A ``diff`` against the ``tutorial_08_data_extraction`` file from :ref:`tutorial_data_extraction_waves` is included below to help identify the
changes made in this tutorial.

.. admonition:: waves-eabm-tutorial/tutorial_09_post_processing

   .. literalinclude:: tutorials_tutorial_09_post_processing
      :language: Python
      :diff: tutorials_tutorial_08_data_extraction

Here we use the ``post_processing.py`` CLI instead of the module's API for the task definition because the
post-processing will include plotting with ``matplotlib``, which is not thread-safe. When the CLI is used, multiple
post-processing tasks from *separate* workflows can be executed in parallel because each task will be launched from a
separate thread. Care must still be taken to ensure that the post-processing tasks do not write to the same files,
however.

**********************
Post-processing script
**********************

4. In the ``waves-eabm-tutorial/eabm_package/python`` directory, create a file called ``post_processing.py`` using the
   contents below.

.. note::

   Depending on the memory and disk resources available and the size of the simulation workflow results, modsim projects
   may need to review the `Xarray`_ documentation for resource management specific to the projects' use case.

.. admonition:: waves-eabm-tutorial/eabm_package/python/post_processing.py

   .. literalinclude:: python_post_processing.py
      :language: Python

The script API and CLI are included in the :ref:`waves_eabm_api`: :ref:`eabm_post_processing_api` and :ref:`waves_eabm_cli`:
:ref:`eabm_post_processing_cli`, respectively.

**********
SConstruct
**********

A ``diff`` against the ``SConstruct`` file from :ref:`tutorial_data_extraction_waves` is included below to help identify the
changes made in this tutorial.

.. admonition:: waves-eabm-tutorial/SConstruct

   .. literalinclude:: tutorials_tutorial_09_post_processing_SConstruct
      :language: Python
      :diff: tutorials_tutorial_08_data_extraction_SConstruct

*************
Build Targets
*************

5. Build the new targets

.. code-block:: bash

   $ pwd
   /path/to/waves-eabm-tutorial
   $ scons tutorial_09_post_processing --jobs=4

************
Output Files
************

6. Observe the catenated parameter results and paramter study dataset in the post-processing task's STDOUT file

.. code-block::

   $ tree build/tutorial_09_post_processing/ -L 1
   build/tutorial_09_post_processing/
   |-- parameter_set0
   |-- parameter_set1
   |-- parameter_set2
   |-- parameter_set3
   |-- parameter_study.h5
   |-- stress_strain_comparison.csv
   |-- stress_strain_comparison.pdf
   `-- stress_strain_comparison.stdout

   4 directories, 4 files
   $ cat build/tutorial_09_post_processing/stress_strain_comparison.stdout
   <xarray.Dataset>
   Dimensions:             (step: 1, time: 5, elements: 1, integration point: 4,
                            E values: 4, parameter_sets: 4, S values: 4,
                            data_type: 1)
   Coordinates:
     * step                (step) object 'Step-1'
     * time                (time) float64 0.0175 0.07094 0.2513 0.86 1.0
     * elements            (elements) int64 1
       integrationPoint    (elements, integration point) float64 1.0 nan nan nan
     * E values            (E values) object 'E11' 'E22' 'E33' 'E12'
     * S values            (S values) object 'S11' 'S22' 'S33' 'S12'
     * parameter_sets      (parameter_sets) <U14 'parameter_set0' ... 'parameter...
     * data_type           (data_type) object 'samples'
       parameter_set_hash  (parameter_sets) object ...
   Dimensions without coordinates: integration point
   Data variables:
       E                   (parameter_sets, step, time, elements, integration point, E values) float32 ...
       S                   (parameter_sets, step, time, elements, integration point, S values) float32 ...
       displacement        (data_type, parameter_sets) float64 ...
       global_seed         (data_type, parameter_sets) float64 ...
       height              (data_type, parameter_sets) float64 ...
       width               (data_type, parameter_sets) float64 ...
