.. _tutorial_cartesian_product_waves:

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

.. _tutorial_cartesian_product_waves_directory_structure:

*******************
Directory Structure
*******************

3. Create a directory ``tutorial_07_cartesian_product`` in the ``waves-eabm-tutorial`` directory.

.. code-block:: bash

   $ pwd
   /path/to/waves-eabm-tutorial
   $ mkdir tutorial_07_cartesian_product

4. Copy the ``tutorial_06_include_files/SConscript`` file into the newly created ``tutorial_07_cartesian_product``
   directory.

.. code-block:: bash

   $ pwd
   /path/to/waves-eabm-tutorial
   $ cp tutorial_06_include_files/SConscript tutorial_07_cartesian_product/

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

5. Create a new file ``eabm_package/python/single_element_compression_cartesian_product.py`` from the content below.

.. admonition:: waves-eabm-tutorial/eabm_package/python/single_element_compression_cartesian_product.py

   .. literalinclude:: python_single_element_compression_cartesian_product.py
      :language: Python

The ``single_element_compression_cartesian_product.py`` file you just created is very similar to the
``single_element_compression_nominal.py`` file from :ref:`tutorial_include_files_waves`. The significant difference
between the two files is the new definition of multiple values for the ``width`` and ``height`` parameters. Also note
that the ``global_seed`` and ``displacement`` parameters are both defined with a ``list``, even though the parameters
only have a single value. The :meth:`waves.parameter_generators.CartesianProduct` API explains this requirement for the
"schema values" to be an iterable.

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
   copy the ``SConscript`` file from :ref:`tutorial_include_files_waves` to the ``tutorial_07_cartesian_product``
   directory. If you prefer, you may start with a blank ``SConscript`` file in the ``tutorial_07_cartesian_product``
   directory and simply copy and paste the contents below into your blank file.

After viewing the full file contents below, continue to read the
:ref:`tutorial_cartesian_product_waves_step_by_step_sconscript_discussion` for building the
``tutorial_07_cartesian_product/SConscript`` file from scratch.

.. admonition:: waves-eabm-tutorial/tutorial_07_cartesian_product/SConscript

   .. literalinclude:: tutorial_07_cartesian_product_SConscript
      :language: Python

.. _tutorial_cartesian_product_waves_step_by_step_sconscript_discussion:

Step-By-Step SConscript Discussion
==================================

.. admonition:: waves-eabm-tutorial/tutorial_07_cartesian_product/SConscript

   .. literalinclude:: tutorial_07_cartesian_product_SConscript
      :language: Python
      :lineno-match:
      :end-before: marker-1
      :emphasize-lines: 7, 10

The beginning portion of the ``SConscript`` file consists of a series of straight forward Python package import
statements. There are, however, two notable lines in the included code above. The first hightlighted line imports the
``parameter_schema`` dictionary into the ``SConscript`` file's name space from the
``single_element_compression_cartesian_product`` module that you created in the
:ref:`tutorial_cartesian_product_waves_parameter_study_file` portion of this tutorial.  The second import line should
look familiar, but is worth pointing out again. Here, we import the ``env`` variable from the parent construction
environment. This will provide access to variables we added to the ``SConstruct`` file's ``project_variables``
dictionary in previous tutorials.

.. admonition:: waves-eabm-tutorial/tutorial_07_cartesian_product/SConscript

   .. literalinclude:: tutorial_07_cartesian_product_SConscript
      :language: Python
      :lineno-match:
      :start-after: marker-1
      :end-before: marker-2
      :emphasize-lines: 5-6, 9-12

The unhighlighted portions of the code snippet above do not present any unique code that has not been previously
discussed.

The highlighted portions of the code snippet above define some new variables that will get used in various places in
this tutorial's code. The ``parameter_study_file`` and ``previous_parameter_study`` will allow the parameter generator
to extend previously executed parameter studies without re-computing existing parameter set output files.

.. admonition:: waves-eabm-tutorial/tutorial_07_cartesian_product/SConscript

   .. literalinclude:: tutorial_07_cartesian_product_SConscript
      :language: Python
      :lineno-match:
      :start-after: marker-2
      :end-before: marker-3

The code above generates the parameter study for this tutorial using the
:meth:`waves.parameter_generators.CartesianProduct` method. The ``parameter_schema`` that was imported in previous code
is used to define the parameter bounds. The ``parameter_study_file`` and ``previous_parameter_study`` will allow the
parameter generator to extend previously executed parameter studies without re-computing existing parameter set output
files on repeat executions of this simulation workflow.

The ``parameter_study`` object is an `xarray dataset`_. For more information about the structure of the
``parameter_generator`` and ``parameter_study`` objects, see the :meth:`waves.parameter_generators.CartesianProduct`
API. The API contains an example that prints ``parameter_study`` and shows the organization of the `xarray dataset`_.
Note that the API's example does not use the same ``parameter_schema`` as this tutorial, but rather a general set of
parameters using different variable types.

The function and task definitions will write the parameter study file to the build directory whenever the parameter
schema file changes. Tasks that execute Python methods require an `SCons Python build function`_, which must be defined
in the configuration file and can't be provided by a `WAVES`_ builder because the parameter generator is instantiated in
the current ``SConscript`` file. The conditional re-write behavior will be important for post-processing tasks
introduced in :ref:`tutorial_post_processing_waves`.

.. admonition:: waves-eabm-tutorial/tutorial_07_cartesian_product/SConscript

   .. literalinclude:: tutorial_07_cartesian_product_SConscript
      :language: Python
      :lineno-match:
      :start-after: marker-3
      :end-before: marker-4

In the ``for`` loop definition above, the ``set_name`` and ``parameters`` variables are defined by iterating on the
``parameter_study`` `xarray dataset`_ (i.e. ``parameter_generator.parameter_study``).  The ``samples`` ``data_type``
coordinate of the ``parameter_study`` is grouped by the coordinate ``parameter_sets``. This will return an iterable to
the ``for`` loop definition that contains the ``set_name`` and the ``parameters`` information. ``parameters`` contains
both the names of the parameters and the parameter values for a given ``set_name``.

Inside the ``for`` loop, the ``set_name`` variable is cast to a `Python pathlib`_ object, as it will aid in constructing
file locations later in the ``SConscript`` file. The suffix is stripped from the set name to separate the parameter set
build directory name from the filenames that would be written by
:meth:`waves.parameter_generators.CartesianProduct.write`, although the method is unused in this tutorial.

Next, the ``parameters`` `xarray dataset`_ is converted to a dictionary. At first declaration, ``simulation_variables``
is a dictionary whose keys are the names of the parameters and whose values are the parameter values for a particular
``set_name``. The same substitution syntax key modification introduced by :ref:`tutorial_parameter_substitution_waves`
is used again when passing the simulation variables dictionary to the :meth:`waves.builders.copy_substitute` method for
text file parameter substitution.

.. admonition:: waves-eabm-tutorial/tutorial_07_cartesian_product/SConscript

   .. literalinclude:: tutorial_07_cartesian_product_SConscript
      :language: Python
      :lineno-match:
      :start-after: marker-4
      :end-before: marker-5

The lines of code above are simply a copy of the previous Geometry, Partition, Mesh, and SolverPrep workflows. Note the
following two important aspects of the code above:

* The indent of four spaces, as this code is inside of the ``for`` loop you created earlier
* The usage of the ``simulation_variables`` dictionary in the ``journal_options`` for Geometry, Partition, and Mesh and
  the :meth:`waves.builders.copy_substitute` method for SolverPrep. Remember to use the
  :meth:`waves.builders.substitution_syntax` method to modify the parameter name keys for parameter substitution in text
  files.

.. admonition:: waves-eabm-tutorial/tutorial_07_cartesian_product/SConscript

   .. literalinclude:: tutorial_07_cartesian_product_SConscript
      :language: Python
      :lineno-match:
      :start-after: marker-5
      :end-before: marker-6

The code above closes out our familiar workflow with the use of the :meth:`waves.builders.abaqus_solver` method. Note
that the ``# Abaqus Solver`` code is still within the ``for`` loop, so the Abaqus Solver will be called as many times as
we have parameter sets. In this case, we will solve four Abaqus simulations.

.. admonition:: waves-eabm-tutorial/tutorial_07_cartesian_product/SConscript

   .. literalinclude:: tutorial_07_cartesian_product_SConscript
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

10. Add ``tutorial_07_cartesian_product`` to the ``eabm_simulation_directories`` list in the
    ``waves-eabm-tutorial/SConstruct`` file.

A ``diff`` against the ``SConstruct`` file from :ref:`tutorial_include_files_waves` is included below to help identify the
changes made in this tutorial.

.. admonition:: waves-eabm-tutorial/SConstruct

   .. literalinclude:: eabm_tutorial_07_cartesian_product_SConstruct
      :language: Python
      :diff: eabm_tutorial_06_include_files_SConstruct

*************
Build Targets
*************

6. Build the new targets

.. code-block:: bash

   $ pwd
   /path/to/waves-eabm-tutorial
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

Explore the contents of the ``build`` directory using the ``tree`` command against the ``build`` directory, as shown
below. Note the usage of ``-I`` to reduce clutter in the ``tree`` command output and the ``-d`` flag to specify only
directories to be shown.

.. code-block:: bash

    $ pwd
    /home/roppenheimer/waves-eabm-tutorial
    $ tree build/ -d -I 'tutorial_0[1,2,3,4,5,6]*'
    build/
    └── tutorial_07_cartesian_product
        ├── parameter_set0
        ├── parameter_set1
        ├── parameter_set2
        └── parameter_set3

    5 directories

Explore the contents of the ``parameter_set0`` directory using the ``tree`` command. The contents of the remaining
``parameter_set{1,2,3}`` directories will be very similar to that shown for ``parameter_set0``.

.. code-block:: bash

    $ pwd
    /home/roppenheimer/waves-eabm-tutorial
    $ tree build/tutorial_07_cartesian_product/parameter_set0
    build/tutorial_07_cartesian_product/parameter_set0
    ├── abaqus.rpy
    ├── abaqus.rpy.1
    ├── abaqus.rpy.2
    ├── amplitudes.inp
    ├── assembly.inp
    ├── boundary.inp
    ├── field_output.inp
    ├── history_output.inp
    ├── materials.inp
    ├── parts.inp
    ├── single_element_compression.abaqus_v6.env
    ├── single_element_compression.com
    ├── single_element_compression.dat
    ├── single_element_compression.inp
    ├── single_element_compression.inp.in
    ├── single_element_compression.msg
    ├── single_element_compression.odb
    ├── single_element_compression.par
    ├── single_element_compression.pes
    ├── single_element_compression.pmg
    ├── single_element_compression.prt
    ├── single_element_compression.sta
    ├── single_element_compression.stdout
    ├── single_element_geometry.abaqus_v6.env
    ├── single_element_geometry.cae
    ├── single_element_geometry.jnl
    ├── single_element_geometry.stdout
    ├── single_element_mesh.abaqus_v6.env
    ├── single_element_mesh.cae
    ├── single_element_mesh.inp
    ├── single_element_mesh.jnl
    ├── single_element_mesh.stdout
    ├── single_element_partition.abaqus_v6.env
    ├── single_element_partition.cae
    ├── single_element_partition.jnl
    └── single_element_partition.stdout

    0 directories, 36 files

The contents of the ``parameter_set0`` directory will appear identical to the contents of the previous tutorials. In
this case, the contents of the files is different, as we have inserted parameters as part of the parameter study.
