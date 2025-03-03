.. _tutorial_mesh_convergence:

##########################
Tutorial: Mesh Convergence
##########################

This tutorial is intended to demonstrate several advanced usage features that were glossed over in previous
tutorials. Specifically, this tutorial will discuss

* Building a parameter study from somewhere in the middle of the SCons workflow using a common source
* Utilizing ``--input-file`` and ``--output-file`` command-line arguments
* Using the ``post_processing.py`` script to create multiple plots

**********
References
**********

* `Mesh Convergence`_ Studies :cite:`ABAQUS`
* SCons file objects: `SCons Node Package`_

***********
Environment
***********

.. include:: tutorial_environment_activation.txt

*******************
Directory Structure
*******************

.. include:: tutorial_directory_setup.txt

.. note::

    If you skipped any of the previous tutorials, run the following commands to create a copy of the necessary tutorial
    files.

    .. code-block:: bash

        $ pwd
        /home/roppenheimer/waves-tutorials
        $ waves fetch --overwrite --tutorial 11 && mv tutorial_11_regression_testing_SConstruct SConstruct
        WAVES fetch
        Destination directory: '/home/roppenheimer/waves-tutorials'

4. Download and copy the ``tutorial_11_regression_testing`` file to a new file named ``tutorial_mesh_convergence``
   with the :ref:`waves_cli` :ref:`waves_fetch_cli` subcommand.

.. code-block:: bash

   $ pwd
   /home/roppenheimer/waves-tutorials
   $ waves fetch --overwrite tutorials/tutorial_11_regression_testing && cp tutorial_11_regression_testing tutorial_mesh_convergence
   WAVES fetch
   Destination directory: '/home/roppenheimer/waves-tutorials'

********************
Parameter Study File
********************

5. Create a new file ``modsim_package/python/rectangle_compression_mesh_convergence.py`` from the content below.

.. admonition:: waves-tutorials/modsim_package/python/rectangle_compression_mesh_convergence.py

   .. literalinclude:: python_rectangle_compression_mesh_convergence.py
      :language: Python

This parameter study will define a mesh convergence study where the global size of the finite elements in the model is
decreased several times by a factor of two.

*************************************
Mesh Convergence Selection Dictionary
*************************************

6. Create a new file ``modsim_package/python/mesh_convergence_stress.yaml`` from the content below.

.. admonition:: waves-tutorials/modsim_package/python/mesh_convergence_stress.yaml

   .. literalinclude:: python_mesh_convergence_stress.yaml

This file defines a YAML formatted dictionary that will be used to change the default data selection of the
``post_processing.py`` script.

**********
SConscript
**********

7. A ``diff`` against the ``tutorial_11_regression_testing`` file from :ref:`tutorial_regression_testing` is
   included below to help identify the changes made in this tutorial. Use the diff to update your
   ``tutorial_mesh_convergence`` file, and then review the paragraphs that follow to understand the meaning of these
   changes.

.. admonition:: waves-tutorials/tutorial_mesh_convergence

   .. literalinclude:: tutorials_tutorial_mesh_convergence
      :language: Python
      :diff: tutorials_tutorial_11_regression_testing

.. admonition:: waves-tutorials/tutorial_mesh_convergence

   .. literalinclude:: tutorials_tutorial_mesh_convergence
      :language: Python
      :lineno-match:
      :end-before: marker-2
      :emphasize-lines: 18, 29-33

The highlighted code above points out two key changes from ``diff`` at the beginning of the file. First, we import the
``parameter_schema`` from the ``rectangle_compression_mesh_convergence.py`` file you created in the beginning of
this tutorial. The second change is the addition of a ``simulation_constants`` dictionary. This parameter study only
changes the meshing ``global_seed`` parameter, and all other model parameters stay constant. One way to achieve this
would be to set the remaining parameters as single-value parameter sets in the ``parameter_schema``. This was done with
the ``global_seed`` and ``displacement`` parameters in :ref:`tutorial_cartesian_product`. Rather, we will set the
``width``, ``height``, and ``displacement`` variables as constants in the ``SConscript`` file, and they will not appear
in the parameter study definition. The individual parameters from the ``parameter_schema`` and ``simulation_constants``
dictionaries will be combined later in the ``SConscript`` file.

.. admonition:: waves-tutorials/tutorial_mesh_convergence

   .. literalinclude:: tutorials_tutorial_mesh_convergence
      :language: Python
      :lineno-match:
      :start-after: marker-3
      :end-before: marker-4
      :emphasize-lines: 4, 13, 19, 24

The code above is largely copy and paste from :ref:`tutorial_regression_testing`, with a few significant
differences:

* The code pertainting to ``# Geometry`` and ``# Partition`` has been moved out of the parameter study's ``for`` loop.
  As this parameter study only involves a meshing parameter, the Geometry and Partition workflow steps need only happen
  once. Then, the mesh convergence parameter study can reuse ``rectangle_partition.cae`` as a common source.
* Note the highlighted lines for the ``target`` definitions in the ``# Geometry`` and ``# Partition`` code. Since this
  code is no longer inside of the ``for`` loop, the ``set_name`` directory has been dropped from the ``target``
  definitions. As the first bullet alluded to, the targets for ``# Geometry`` and ``# Partition`` will be built in the
  overall build directory, ``build/tutorial_mesh_convergence``.
* The following highlighted line is necessary for the parameterized ``# Mesh`` workflow steps to reuse a common
  target. The SCons file object for the ``rectangle_partition.cae`` file is extracted from the target list,
  ``partition_target``, as a source.
* The final highlighted line shows how the ``simulation_variables`` dictionary is constructed by combining the
  ``simulation_constants`` and the ``global_seed`` parameters for every simulation.

.. admonition:: waves-tutorials/tutorial_mesh_convergence

   .. literalinclude:: tutorials_tutorial_mesh_convergence
      :language: Python
      :lineno-match:
      :start-after: marker-4
      :end-before: marker-5
      :emphasize-lines: 3, 14

The highlighted lines above demonstrate the usage of ``--input-file`` and ``--output--file`` command-line arguments for
the ``rectangle_mesh.py`` file. In previous tutorials, we have accepted the default values for input and output
files. In this case, however, we must specify that a common input file is used, as we want to reuse the target from the
``Partition`` task as a source. If we would have accepted the default input file name, the ``rectangle_mesh.py``
script would try to open a ``rectangle_partition.cae`` file in every parameter set build directory. The script
would fail to do so, because ``rectangle_partition.cae`` resides a directory above in the main build directory. We
avoid this issue by providing the absolute path to ``rectangle_partition.cae`` as the ``--input-file``.

The ``--output-file`` command-line argument is specified in this case only for demonstration (the default value would
actually work just fine).

The highlighted line containing ``partition_cae_object`` demonstrates the usage of an ``SCons`` file object as a source.
Rather than pointing to the ``rectangle_partition.cae`` file via absolute path, we can let ``SCons`` find the file
for us in the build directory. This is achieved by simply pointing to the ``SCons`` file object that was created when we
specified ``rectangle_partition.cae`` as a target in the ``# Partition`` workflow.

.. admonition:: waves-tutorials/tutorial_mesh_convergence

   .. literalinclude:: tutorials_tutorial_mesh_convergence
      :language: Python
      :lineno-match:
      :start-after: marker-6
      :emphasize-lines: 17-35

The highlighted code above demonstrated the usage of the ``post_processing.py`` script to generate a second plot. The first
plot, as demonstrated in :ref:`tutorial_post_processing`, is a simple stress-strain comparison for each parameter
set. The highlighted code is used to generate a plot of global mesh size versus the stress in the model at the end of
the simulation. As the global mesh size decreases, the final stress should start to converge to a common value.

The specification of a ``selection_dict`` demonstrates another feature of the ``post_processing.py`` command-line
interface. In this case, the only ``key: value`` pair added to the ``selection_dict`` that does not already exist in the
:ref:`post_processing_cli` CLI defaults is the specification of the time point ``'time': 1.0``. This down selects
our data to the largest compressive stress produced by the simulation, which will be our quantity of interest (QoI) for
this simulation workflow.

The remaining changes are rather simple. The ``--x-units`` and ``--x-var`` command-line arguments are updated to reflect
the usage of the ``global_seed`` parameter as the independent variable.

**********
SConstruct
**********

8. A ``diff`` against the ``SConstruct`` file from :ref:`tutorial_regression_testing` is included below to help
   identify the changes made in this tutorial. Make these changes to your ``SConstruct`` file.

.. admonition:: waves-tutorials/SConstruct

   .. literalinclude:: tutorials_tutorial_mesh_convergence_SConstruct
      :language: Python
      :diff: tutorials_tutorial_11_regression_testing_SConstruct

*************
Build Targets
*************

9. Build the new targets

.. code-block:: bash

   $ pwd
   /home/roppenheimer/waves-tutorials
   $ scons tutorial_mesh_convergence --jobs=4

The output from building the targets is not shown explicitly here, but look for one particular thing in your terminal
output. You should notice the execution of the ``rectangle_geometry.py`` and ``rectangle_partition.py``
scripts first, and then the parameter study is kicked off with multiple executions of the ``rectangle_mesh.py``
script.

************
Output Files
************

10. Observe the catenated parameter results and parameter study dataset in the post-processing task's STDOUT file.

.. code-block::

    $ cat build/tutorial_mesh_convergence/mesh_convergence_stress.stdout

    <xarray.Dataset>
    Dimensions:              (E values: 4, S values: 4, elements: 64, step: 1,
                             time: 5, set_name: 4)
    Coordinates:
      * E values            (E values) object 'E11' 'E22' 'E33' 'E12'
      * S values            (S values) object 'S11' 'S22' 'S33' 'S12'
      * elements            (elements) int64 1 2 3 4 5 6 7 ... 58 59 60 61 62 63 64
      * step                (step) object 'Step-1'
      * time                (time) float64 0.0175 0.07094 0.2513 0.86 1.0
        integrationPoint    (set_name, elements) float64 1.0 nan ... 1.0 1.0
      * set_name            (set_name) <U14 'parameter_set0' ... 'parameter...
        set_hash            (set_name) object ...
    Data variables:
        E                   (set_name, step, time, elements, E values) float32 ...
        S                   (set_name, step, time, elements, S values) float32 ...
        global_seed         (set_name) float64 ...
