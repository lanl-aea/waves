.. _tutorial_cartesian_product:

##############################
Tutorial 07: Cartesian Product
##############################

**********
References
**********

* |PROJECT| :ref:`parameter_generator_api` API: :meth:`waves.parameter_generators.CartesianProduct`
* `Cartesian Product`_
* `Xarray`_ and the `xarray dataset`_ :cite:`xarray,hoyer2017xarray`

***********
Environment
***********

.. include:: tutorial_environment_activation.txt

.. include:: version_check_warning.txt

.. _tutorial_cartesian_product_waves_directory_structure:

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
        $ waves fetch --overwrite --tutorial 6 && mv tutorial_06_include_files_SConstruct SConstruct
        WAVES fetch
        Destination directory: '/home/roppenheimer/waves-tutorials'

4. Download and copy the ``tutorial_06_include_files`` file to a new file named ``tutorial_07_cartesian_product``
   with the :ref:`waves_cli` :ref:`waves_fetch_cli` subcommand.

.. code-block:: bash

   $ pwd
   /home/roppenheimer/waves-tutorials
   $ waves fetch --overwrite tutorials/tutorial_06_include_files && cp tutorial_06_include_files tutorial_07_cartesian_product
   WAVES fetch
   Destination directory: '/home/roppenheimer/waves-tutorials'

.. _tutorial_cartesian_product_waves_parameter_study_file:

********************
Parameter Study File
********************

In this tutorial, we will use an included parameter study python file to define a parameter study using a `Cartesian
Product`_ sampling methodology.

.. admonition:: What is Cartesian Product

   A "cartesian product" is a set of all ordered pairs of the elements for a series of list objects. Another commonly
   used synonym for `Cartesian Product`_ is *Full Factorial*.

   Take a parameter study defined by variables ``A`` which has three samples, ``B`` which has two samples, and ``C``
   which has one sample. The result will be a parameter study that contains six (``3x2x1``) simulations.

   For more information, see this `Cartesian Product`_ Wiki page.

5. Create a new file ``modsim_package/python/rectangle_compression_cartesian_product.py`` from the content below.

.. admonition:: waves-tutorials/modsim_package/python/rectangle_compression_cartesian_product.py

   .. literalinclude:: python_rectangle_compression_cartesian_product.py
      :language: Python

The ``rectangle_compression_cartesian_product.py`` file you just created is very similar to the
``rectangle_compression_nominal.py`` file from :ref:`tutorial_include_files`. The significant difference between
the two files is the new definition of multiple values for the ``width`` and ``height`` parameters. Also note that the
``global_seed`` and ``displacement`` parameters are both defined with a ``list``, even though the parameters only have a
single value. The :meth:`waves.parameter_generators.CartesianProduct` API explains this requirement for the "schema
values" to be an iterable. You can view the parameter schema documentation in the :ref:`waves_tutorial_api` for
:ref:`python_rectangle_compression_cartesian_product_api`.

In the ``parameter_schema``, we have defined two parameters with two samples each and two parameters with one sample
each. This will result in four (``2x2x1x1``) total simulations.

**********
SConscript
**********

The ``diff`` for changes in the ``SConscript`` file for this tutorial is extensive because of the for loop indent
wrapping the task generation for each parameter set. For convenience, the full source file is included below to aid in a
wholesale copy and paste when creating the new ``SConscript`` file.

.. note::

   In the :ref:`tutorial_cartesian_product_waves_directory_structure` section of this tutorial, you were instructed to
   copy the ``tutorial_06_include_files`` file to the ``tutorial_07_cartesian_product`` file. If you prefer, you may
   start with a blank ``tutorial_07_cartesian_product`` file and simply copy and paste the contents below into your
   blank file.

After viewing the full file contents below, continue to read the
:ref:`tutorial_cartesian_product_waves_step_by_step_sconscript_discussion` for building the
``tutorial_07_cartesian_product`` file from scratch.

.. admonition:: waves-tutorials/tutorial_07_cartesian_product

   .. literalinclude:: tutorials_tutorial_07_cartesian_product
      :language: Python

.. _tutorial_cartesian_product_waves_step_by_step_sconscript_discussion:

Step-By-Step SConscript Discussion
==================================

.. admonition:: waves-tutorials/tutorial_07_cartesian_product

   .. literalinclude:: tutorials_tutorial_07_cartesian_product
      :language: Python
      :lineno-match:
      :end-before: marker-1
      :emphasize-lines: 16, 19

The beginning portion of the ``SConscript`` file consists of a series of straight forward Python package import
statements. There are, however, two notable lines in the included code above. The first hightlighted line imports the
``parameter_schema`` dictionary into the ``SConscript`` file's name space from the
``rectangle_compression_cartesian_product`` module that you created in the
:ref:`tutorial_cartesian_product_waves_parameter_study_file` portion of this tutorial.  The second import line should
look familiar, but is worth pointing out again. Here, we import the ``env`` variable from the parent construction
environment. This will provide access to variables we added to the ``SConstruct`` file's ``project_variables``
dictionary in previous tutorials.

.. admonition:: waves-tutorials/tutorial_07_cartesian_product

   .. literalinclude:: tutorials_tutorial_07_cartesian_product
      :language: Python
      :lineno-match:
      :start-after: marker-1
      :end-before: marker-2

Most of the code snippet has been seen before. The ``parameter_study_file`` variable will allow the parameter generator
to extend previously executed parameter studies without re-computing existing parameter set output files.

.. admonition:: waves-tutorials/tutorial_07_cartesian_product

   .. literalinclude:: tutorials_tutorial_07_cartesian_product
      :language: Python
      :lineno-match:
      :start-after: marker-2
      :end-before: marker-3

The code above generates the parameter study for this tutorial using the
:meth:`waves.parameter_generators.CartesianProduct` method. The ``parameter_schema`` that was imported in previous code
is used to define the parameter bounds. The ``parameter_study_file`` will allow the parameter generator to extend
previously executed parameter studies without re-computing existing parameter set output files on repeat executions of
this simulation workflow.

The ``parameter_generator.parameter_study`` object is an `xarray dataset`_. For more information about the structure of the
``parameter_generator`` and ``parameter_study`` objects, see the :meth:`waves.parameter_generators.CartesianProduct`
API. The API contains an example that prints ``parameter_study`` and shows the organization of the `xarray dataset`_.
Note that the API's example does not use the same ``parameter_schema`` as this tutorial, but rather a general set of
parameters using different variable types.

At configuration time, the :meth:`waves.parameter_generators.CartesianProduct.write` method will write the parameter
study file whenever the contents of the parameter study have changed. The contents check is performed against the
``previous_parameter_study`` file if it exists. The conditional re-write behavior will be important for
post-processing tasks introduced in :ref:`tutorial_post_processing`.

.. admonition:: waves-tutorials/tutorial_07_cartesian_product

   .. literalinclude:: tutorials_tutorial_07_cartesian_product
      :language: Python
      :lineno-match:
      :start-after: marker-3
      :end-before: marker-4

In the ``for`` loop definition above, the ``set_name`` and ``parameters`` variables are defined by iterating on the
``parameter_study`` `xarray dataset`_ (i.e. ``parameter_generator.parameter_study``). The
:meth:`waves.parameter_generators.CartesianProduct.parameter_study_to_dict` method will return an iterable to the
``for`` loop definition that contains the ``set_name`` and the ``parameters`` information. ``parameters`` contains both
the names of the parameters and the parameter values for a given ``set_name``.

Inside the ``for`` loop, the ``set_name`` variable is cast to a `Python pathlib`_ object, as it will aid in constructing
file locations later in the ``SConscript`` file. The suffix is stripped from the set name to separate the parameter set
build directory name from the filenames that would be written by
:meth:`waves.parameter_generators.CartesianProduct.write`, although the method is unused in this tutorial.

Next, the ``parameters`` `xarray dataset`_ is converted to a dictionary. At first declaration, ``simulation_variables``
is a dictionary whose keys are the names of the parameters and whose values are the parameter values for a particular
``set_name``. The same substitution syntax key modification introduced by :ref:`tutorial_parameter_substitution`
is used again when passing the simulation variables dictionary to the :meth:`waves.scons_extensions.copy_substfile` method for
text file parameter substitution.

.. admonition:: waves-tutorials/tutorial_07_cartesian_product

   .. literalinclude:: tutorials_tutorial_07_cartesian_product
      :language: Python
      :lineno-match:
      :start-after: marker-4
      :end-before: marker-5
      :emphasize-lines: 4, 14-15, 25-27, 29, 49

The lines of code above are nearly a direct copy of the previous Geometry, Partition, Mesh, and SolverPrep workflows.
Note the following two important aspects of the code above:

* The indent of four spaces, as this code is inside of the ``for`` loop you created earlier
* Target files must be defined with respect to their parameter set directory, which will be created in the current
  simulation build directory. Any targets that are later used as source must also include the parameter set directory as
  part of their relative path.
* The usage of the ``simulation_variables`` dictionary in the ``subcommand_options`` for Geometry, Partition, and Mesh and
  the :meth:`waves.scons_extensions.copy_substfile` method for SolverPrep. Remember to use the
  :meth:`waves.scons_extensions.substitution_syntax` method to modify the parameter name keys for parameter substitution in text
  files.

.. admonition:: waves-tutorials/tutorial_07_cartesian_product

   .. literalinclude:: tutorials_tutorial_07_cartesian_product
      :language: Python
      :lineno-match:
      :start-after: marker-5
      :end-before: marker-6

The code above closes out our familiar workflow with the use of the
:meth:`waves.scons_extensions.abaqus_solver_builder_factory` method where the task definitions have changed to include
the parameter set directory, ``set_name``, as part of source and target definitions. Note that the ``# Abaqus Solver``
code is still within the ``for`` loop, so the Abaqus Solver will be called as many times as we have parameter sets. In
this case, we will solve four Abaqus simulations.

.. admonition:: waves-tutorials/tutorial_07_cartesian_product

   .. literalinclude:: tutorials_tutorial_07_cartesian_product
      :language: Python
      :lineno-match:
      :start-after: marker-6

The final additions to the ``SConscript`` file are a few lines of code that are directly copy-and-pasted from your
previous tutorial ``SConscript`` file. Note, however, that these final lines of code are outside of the ``for`` loop
that contained the previous snippets of code. These final lines of code exists outside the ``for`` loop because we want
to include the *tasks for all parameter sets* in the convenience alias, ``tutorial_07_cartesian_product``.

**********
SConstruct
**********

6. Add ``tutorial_07_cartesian_product`` to the ``workflow_configurations`` list in the
   ``waves-tutorials/SConstruct`` file.

A ``diff`` against the ``SConstruct`` file from :ref:`tutorial_include_files` is included below to help identify the
changes made in this tutorial.

.. admonition:: waves-tutorials/SConstruct

   .. literalinclude:: tutorials_tutorial_07_cartesian_product_SConstruct
      :language: Python
      :diff: tutorials_tutorial_06_include_files_SConstruct

*************
Build Targets
*************

7. Build the new targets

.. code-block:: bash

   $ pwd
   /home/roppenheimer/waves-tutorials
   $ scons tutorial_07_cartesian_product --jobs=4
   <output truncated>

In the command above, `SCons`_ is instructed to use four threads to build this tutorial's targets. For this tutorial,
four ``jobs`` is a sensible number, as we have four simulations to run that are independent of each other downstream
from parameter set generation. By using the ``--jobs=4`` option, `SCons`_ can run all four simulations in parallel.

.. warning::

   Be aware of the difference between `SCons`_ thread management and task threading requests. `SCons`_ only manages
   thread count (CPU) usage for task execution and does not control multi-threaded tasks. For example, if you specify
   ``scons --jobs=4``, `SCons`_ will use four worker threaders to execute task actions in parallel. If each of the four
   tasks also specifies multi-threading, `SCons`_ will **not** balance the requested CPU count for each task with the
   four worker threads already in use. An example of this is running Abaqus simulations on multiple CPUs, e.g.
   ``abaqus_options='-cpus 12'``. In this case, four worker threads that execute tasks each requesting 12 CPUs will
   result in the consumption of ``4+4*12`` CPUs.

************
Output Files
************

Explore the contents of the ``build`` directory using the ``ls`` and ``tree`` commands against the ``build`` directory,
as shown below.

.. code-block:: bash

    $ pwd
    /home/roppenheimer/waves-tutorials
    $ ls build/tutorial_07_cartesian_product/
    parameter_set0/  parameter_set1/  parameter_set2/  parameter_set3/  parameter_study.h5

Explore the contents of the ``parameter_set0`` directory using the ``tree`` command. The contents of the remaining
``parameter_set{1,2,3}`` directories will be very similar to that shown for ``parameter_set0``.

.. code-block:: bash

   $ pwd
   /home/roppenheimer/waves-tutorials
   $ tree build/tutorial_07_cartesian_product/parameter_set0/
   build/tutorial_07_cartesian_product/parameter_set0/
   |-- abaqus.rpy
   |-- abaqus.rpy.1
   |-- abaqus.rpy.2
   |-- assembly.inp
   |-- boundary.inp
   |-- field_output.inp
   |-- history_output.inp
   |-- materials.inp
   |-- parts.inp
   |-- rectangle_compression.com
   |-- rectangle_compression.dat
   |-- rectangle_compression.inp
   |-- rectangle_compression.inp.in
   |-- rectangle_compression.msg
   |-- rectangle_compression.odb
   |-- rectangle_compression.prt
   |-- rectangle_compression.sta
   |-- rectangle_compression.stdout
   |-- rectangle_geometry.cae
   |-- rectangle_geometry.jnl
   |-- rectangle_geometry.stdout
   |-- rectangle_mesh.cae
   |-- rectangle_mesh.inp
   |-- rectangle_mesh.jnl
   |-- rectangle_mesh.stdout
   |-- rectangle_partition.cae
   |-- rectangle_partition.jnl
   `-- rectangle_partition.stdout

   0 directories, 28 files

The contents of the ``parameter_set0`` directory will appear identical to the contents of the previous tutorials. In
this case, the contents of the files is different, as we have inserted parameters as part of the parameter study.

**********************
Workflow Visualization
**********************

View the workflow directed graph by running the following command and opening the image in your preferred image viewer.
First, plot the workflow with all parameter sets.

.. code-block::

   $ pwd
   /home/roppenheimer/waves-tutorials
   $ waves visualize tutorial_07_cartesian_product --output-file tutorial_07_cartesian_product.png --width=40 --height=12 --exclude-list /usr/bin .stdout .jnl .prt .com .msg .dat .sta

The output should look similar to the figure below.

.. raw:: latex

    \begin{landscape}
        \vspace*{\fill}

.. figure:: tutorial_07_cartesian_product.png
   :align: center
   :width: 100%

.. raw:: latex

        \vspace*{\fill}
    \end{landscape}

In this figure we begin to see the value of a build system for modsim execution. Despite excluding most of the
simulation output files, the full parameter study directed graph is much larger than the one shown in
:ref:`tutorial_include_files`. With the piecewise construction of the input deck standing in for a moderately complex
modsim project, even a four set parameter study quickly grows unmanageable for manual state tracking and execution. With
`SCons`_ managing the directed graph construction, state, and execution, the modsim developer can focus attention on the
engineering analysis and benefit from partial re-execution of the parameter study when only a subset of the parameter
study has changed.

Now plot the workflow with only the first set, ``set0``.

.. code-block::

   $ pwd
   /home/roppenheimer/waves-tutorials
   $ waves visualize tutorial_07_cartesian_product --output-file tutorial_07_cartesian_product_set0.png --width=42 --height=6 --exclude-list /usr/bin .stdout .jnl .prt .com .msg .dat .sta --exclude-regex "set[1-9]"

The output should look similar to the figure below.

.. raw:: latex

    \begin{landscape}
        \vspace*{\fill}

.. figure:: tutorial_07_cartesian_product_set0.png
   :align: center
   :width: 100%

.. raw:: latex

        \vspace*{\fill}
    \end{landscape}

While the first image is useful for demonstrating modsim project size and scope, a more useful directed graph can be
evaluated by limiting the output to a single set. This image should look similar to the
:ref:`tutorial_include_files` directed graph, but with fewer output files because the ``*.msg``, ``*.dat``, and
``*.sta`` files have been excluded to make the full parameter study graph more readable.
