.. _waves_quickstart:

####################
|PROJECT| Quickstart
####################

This quickstart will create a minimal, two file project configuration combining elements of the tutorials listed below.

* :ref:`tutorialsconstruct`
* :ref:`tutorial_geometry`
* :ref:`tutorial_partition_mesh`
* :ref:`tutorial_solverprep`
* :ref:`tutorial_simulation`
* :ref:`tutorial_parameter_substitution`
* :ref:`tutorial_cartesian_product`
* :ref:`tutorial_post_processing`

These tutorials and this quickstart describe the computational engineering workflow through simulation execution and
post-processing. This tutorial will use a different working directory and directory structure than the rest of the
tutorials to avoid filename clashes.

***********
Environment
***********

.. include:: tutorial_environment_activation.txt

.. include:: version_check_warning.txt

*******************
Directory Structure
*******************

3. Create the project directory structure and copy the `WAVES quickstart source files`_ into the ``~/waves-tutorials/waves_quickstart``
   sub-directory with the :ref:`waves_cli` :ref:`waves_fetch_cli` subcommand.

.. code-block:: bash

      $ waves fetch tutorials/waves_quickstart --destination ~/waves-tutorials/waves_quickstart
      WAVES fetch
      Destination directory: '/home/roppenheimer/waves-tutorials/waves_quickstart'
      $ cd ~/waves-tutorials/waves_quickstart
      $ pwd
      /home/roppenheimer/waves-tutorials/waves_quickstart

**********
SConscript
**********

Managing digital data and workflows in modern computational science and engineering is a difficult and error-prone task.
The large number of steps in the workflow and complex web of interactions between data files results in non-intuitive
dependencies that are difficult to manage by hand. This complexity grows substantially when the workflow includes
parameter studies. |PROJECT| enables the use of traditional software build systems in computational science and
engineering workflows with support for common engineering software and parameter study management and compatibility.

Build systems construct `directed acyclic graph`_ (DAG) from small, granular task definitions. Each task is defined by
the developer and subsequently linked by the build system. Tasks are composed of targets, sources, and actions. A target
is the output of the task. Sources are the required direct-dependency files used by the task and may be files tracked by
the version control system for the project or files produced by other tasks. Actions are the executable commands that
produce the target files. In pseudocode, this might look like a dictionary:

.. code-block:: YAML

   task1:
       target: output1
       source: source1
       action: action1 --input source1 --output output1

   task2:
       target: output2
       source: output1
       action: action2 --input output1 --output output2

As the number of discrete tasks increases, and as cross-dependencies grow, an automated tool to construct the build
order becomes more important. Besides simplifying the process of constructing the workflow DAG, most build systems also
incorporate a state machine. The build system tracks the execution state of the DAG and will only re-build out-of-date
portions of the DAG. This is especially valuable when trouble-shooting or expanding a workflow. For instance, when
adding or modifying the post-processing step, the build system will not re-run simulation tasks that are computationally
expensive and require significant wall time to solve.

The ``SConscript`` file below contains the workflow task definitions. Review the source and target files defining the
workflow tasks. As discussed briefly above and in detail in :ref:`build_system`, a task definition also requires an
action. For convenience, |PROJECT| provides builders for common engineering software with pre-defined task actions.
See the :meth:`waves.scons_extensions.abaqus_journal_builder_factory` and :meth:`waves.scons_extensions.abaqus_solver`
for more complete descriptions of the builder actions.

.. admonition:: waves_quickstart/SConscript

    .. literalinclude:: waves_quickstart_SConscript
       :language: Python
       :lineno-match:

**********
SConstruct
**********

For this quickstart, we will not discuss the main SCons configuration file, named ``SConstruct``, in detail.
:ref:`tutorialsconstruct` has a more complete discussion about the contents of the ``SConstruct`` file.

One of the primary benefits to |PROJECT| is the ability to robustly integrate the conditional re-building behavior of a
build system with computational parameter studies. Because most build systems consist of exactly two steps:
configuration and execution, the full DAG must be fixed at configuration time. To avoid hardcoding the parameter study
tasks, it is desirable to re-use the existing workflow or task definitions. This could be accomplished with a simple for
look and naming convention; however, it is common to run a small, scoping parameter study prior to exploring the full
parameter space.

To avoid out-of-sync errors in parameter set definitions when updating a previously executed parameter study, |PROJECT|
provides a parameter study generator utility that uniquely identifies parameter sets by contents, assigns a unique index
to each parameter set, and guarantees that previously executed sets are matched to their unique identifier. When
expanding or re-executing a parameter study, |PROJECT| enforces set name/content consistency which in turn ensures that
the build system can correctly identify previous work and only re-build the new or changed sets.

In the configuration snippet below, the workflow parameterization is performed in the root configuration file,
``SConstruct``. This allows us to re-use the entire workflow file, ``SConscript``, with more than one parameter study.
First, we define a nominal workflow. Single set studies can be defined as a simple dictionary. This can be useful for
trouble-shooting the workflow, simulation definition, and simulation convergence prior to running a larger parameter
study. Second, we define a small mesh convergence study where the only parameter that changes is the mesh global seed.

.. admonition:: waves_quickstart/SConstruct

    .. literalinclude:: waves_quickstart_SConstruct
       :language: Python
       :lineno-match:
       :start-at: # Define parameter studies
       :end-before: # Add workflow(s)

Finally, we call the workflow ``SConscript`` file in a loop where the study names definitions are unpacked into the
workflow call. The ``ParameterStudySConscript`` method handles the differences between a nominal dictionary parameter
set and the mesh convergence parameter study object. The ``SConscript`` file has been written to accept the
``parameters`` variable that will be unpacked by this function.

.. admonition:: waves_quickstart/SConstruct

    .. literalinclude:: waves_quickstart_SConstruct
       :language: Python
       :lineno-match:
       :start-at: # Add workflow(s)
       :end-before: # List all aliases in help message

In this tutorial, the entire workflow is re-run from scratch for each parameter set. This simplifies the parameter study
construction and enables the geometric parameterization hinted at in the ``width`` and ``height`` parameters. Not all
workflows require the same level of granularity and re-use. There are resource trade-offs to workflow construction, task
definition granularity, and computational resources. For instance, if the geometry and partition tasks required
significant wall time, but are not part of the mesh convergence study, it might be desirable to parameterize within the
``SConscript`` file where the geometry and partition tasks could be excluded from the parameter study.

|PROJECT| provides several solutions for paramterizing at the level of workflow files, task definitions, or in arbitrary
locations and methods, depending on the needs of the project.

* workflow files: :meth:`waves.scons_extensions.parameter_study_sconscript`
* task definitions: :meth:`waves.scons_extensions.parameter_study`
* anywhere: :meth:`waves.parameter_generators.ParameterGenerator.parameter_study_to_dict`

****************
Building targets
****************

.. code-block::

   $ pwd
   /home/roppenheimer/waves-tutorials/waves_quickstart
   $ scons nominal

************
Output Files
************

.. code-block:: bash

   $ pwd
   /home/roppenheimer/waves-tutorials/waves_quickstart
   $ tree build/nominal
   build/nominal
   |-- SConscript
   |-- abaqus.rpy
   |-- abaqus.rpy.1
   |-- abaqus.rpy.2
   |-- abaqus_utilities.py
   |-- abaqus_utilities.pyc
   |-- post_processing.py
   |-- rectangle_compression.abaqus_v6.env
   |-- rectangle_compression.com
   |-- rectangle_compression.csv
   |-- rectangle_compression.dat
   |-- rectangle_compression.h5
   |-- rectangle_compression.inp
   |-- rectangle_compression.inp.in
   |-- rectangle_compression.msg
   |-- rectangle_compression.odb
   |-- rectangle_compression.prt
   |-- rectangle_compression.sta
   |-- rectangle_compression.stdout
   |-- rectangle_compression_datasets.h5
   |-- rectangle_geometry.cae
   |-- rectangle_geometry.cae.stdout
   |-- rectangle_geometry.jnl
   |-- rectangle_geometry.py
   |-- rectangle_mesh.cae
   |-- rectangle_mesh.inp
   |-- rectangle_mesh.inp.stdout
   |-- rectangle_mesh.jnl
   |-- rectangle_mesh.py
   |-- rectangle_partition.cae
   |-- rectangle_partition.cae.stdout
   |-- rectangle_partition.jnl
   |-- rectangle_partition.py
   |-- stress_strain.csv
   |-- stress_strain.pdf
   `-- stress_strain.pdf.stdout

   0 directories, 36 files

**********************
Workflow Visualization
**********************

To visualize the workflow, you can use the |project| :ref:`waves_visualize_cli` command. The ``--output-file`` allows
you to save the visualization file non-interactively. Without this option, you'll enter an interactive matplotlib window.

.. code-block::

   $ pwd
   /home/roppenheimer/waves-tutorials/waves_quickstart
   $ waves visualize nominal --output-file waves_quickstart.png --width=30 --height=6

The workflow visualization should look similar to the image below, which is a representation of the directed graph
constructed by `SCons`_ from the task definitions. The image starts with the final workflow target on the left, in this
case the ``nominal`` simulation target alias. Moving left to right, the files required to complete the workflow are
shown until we reach the original source file(s) on the far right of the image. The arrows represent actions and are
drawn from a required source to the produced target. The :ref:`computational_tools` introduction discusses the
relationship of a :ref:`build_system` task and :ref:`build_system_directed_graphs`.

.. raw:: latex

    \begin{landscape}
        \vspace*{\fill}

.. figure:: waves_quickstart.png
   :align: center
   :width: 100%

.. raw:: latex

        \vspace*{\fill}
    \end{landscape}
