.. _tutorial_cartesian_product_waves:

##############################
Tutorial 07: Cartesian Product
##############################

**********
References
**********

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

In this tutorial, we will use an included parameter study python file to define a parmetet study using a `Cartesian 
Product`_ sampling methodology.

.. admonition:: What is Cartesian Product
   
   A "cartesian product" is a set of all ordered pairs of the elements for a series of list objects. Another commonly 
   used synonym for `Cartesian Product`_ is *Full Factorial*.

   Take a parameter study defined by variables ``A`` which has three samples, ``B`` which has two samples, and ``C`` 
   which has one sample. The result will be a parameter study that contains six (``3x2x1``) simulations.
   
   For more information, see this `Cartesian Product`_ Wiki page.

5. Create a new file ``eabm_package/python/tutorial_07_cartesian_product.py`` from the content below.

.. admonition:: waves-eabm-tutorial/eabm_package/python/tutorial_07_cartesian_product.py

   .. literalinclude:: python_tutorial_07_cartesian_product.py 
      :language: Python 

The ``tutorial_07_cartesian_product.py`` file you just created is very similar to the 
``single_element_compression_nominal.py`` file from :ref:`tutorial_include_files_waves`. The significant difference 
between the two files is the new definition of multiple values for the ``width`` and ``height`` parameters.

In the ``parameter_schema``, we have defined two parameters with two samples each and two parameters with one sample 
each. This will result in four total simulations.

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

After viewing the full file contents below, continue to read the step by step procedure for building the 
``tutorial_07_cartesian_product/SConscript`` file from scratch.

.. admonition:: waves-eabm-tutorial/tutorial_07_cartesian_product/SConscript

   .. literalinclude:: tutorial_07_cartesian_product_SConscript
      :language: Python

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
``parameter_schema`` dictioanry into the ``SConscript`` file's name space from the ``tutorial_07_cartesian_product`` 
module that you created in the :ref:`tutorial_cartesian_product_waves_parameter_study_file` portion of this tutorial. 
The second import line should look familiar, but is worth pointing out again. Here, we import the ``env`` variable from 
the parent construction environment. This will provide access to variables we added to the ``SConstruct`` file's 
``project_variables`` dictionary in previous tutorials.

.. admonition:: waves-eabm-tutorial/tutorial_07_cartesian_product/SConscript

   .. literalinclude:: tutorial_07_cartesian_product_SConscript
      :language: Python
      :lineno-match:
      :start-after: marker-1
      :end-before: marker-2
      :emphasize-lines: 6-8

The unhighlighted portions of the code snippet above do not present any unique code that has not been previously 
discussed.

The highlighted portions of the code snippet above define some new variables that will get used in various places in 
this tutorial's code. The ``current_build_directory`` is the absolute path of the directory where the ``SConscript`` 
lives and is constructed as a `Python pathlib`_ object. The ``parameter_set_file_template`` defines how the parameter 
sets, and subsequently the directories for each parametized simulation, will be named.

.. admonition:: waves-eabm-tutorial/tutorial_07_cartesian_product/SConscript

   .. literalinclude:: tutorial_07_cartesian_product_SConscript
      :language: Python
      :lineno-match:
      :start-after: marker-2
      :end-before: marker-3

The code above generates the parameter study for this tutorial, using the 
:meth:`waves.parameter_generators.CartesianProduct` method. The ``parameter_schema`` that was imported in previous code 
is used to define the parameter bounds, and the ``output_file_template`` option defines how the parameter set output 
files will be named, and subsequently how the parameter sets will be accessed in the ``parameter_study`` object. The 
``parameter_study`` object is an `xarray dataset`_. Follow the tip below for exploring the structure of the parameter 
study.

The parameter ``set_names`` are extracted from the `xarray dataset`_, converted to `Python pathlib`_ objects, and stored 
in a ``list`` container. We will iterate through this list in upcomming code to execute our parameter study. Lastly, the 
``parameter_names`` are extracted from the `xarray dataset`_ as a ``list``. This ``list`` will be used to formulate the 
``simulation_variables`` dictionary like in :ref:`tutorial_parameter_substitution_waves`.

.. tip::

   Explore the variable types and contents of the ``parameter_generator`` and ``parameter_study`` variables. In the next 
   additions to the ``SConscript`` file, you will add code to parse the ``parameter_study`` object to create the 
   ``simulation_variables`` parmeter substitution dictionary. Understanding the structure of the 
   ``parameter_study`` `xarray dataset`_ will help clarify this process.

   
   1. Create a file called ``tutorial_07_cartesian_product/examine_parameter_study_object.py`` using the contents shown 
      below.

   .. admonition:: waves-eabm-tutorial/tutorial_07_cartesian_product/examine_parameter_study_object.py
   
      .. literalinclude:: tutorial_07_cartesian_product_examine_parameter_study_object.py
         :language: Python
         :lineno-match:

   The ``examine_parameter_study_object.py`` file does the following:
   
   * Import the ``waves`` package (note the comment above the ``import`` statments when importing from outside the 
     WAVES repository)
   * Create a sample ``parameter_schema`` dictionary. Note that in this tutorial, we import this from a module file 
     instead.
   * Generate the parameter sets with a ``parameter_generator``
   * Extract the ``parameter_study`` `xarray dataset`_ from the ``parameter_generator`` object
   * Print some information about the ``parameter_generator`` and ``parameter_study`` variables

   2. From within the ``tutorial_07_cartesian_product`` directory, execute the ``examine_parameter_study_object.py`` 
      file using Python.

      .. literalinclude:: tutorial_07_cartesian_product_parameter_study_message.txt
   
   The first two printed lines display the variable types of the ``parameter_generator`` and ``parameter_study`` 
   variables. The remainig text is the output from printing the ``parameter_study`` `xarray dataset`_. The coordinates 
   of the ``parameter_study`` object provide the names of the parameters and metadata associated with the parameters. In 
   this case, the parameter study ``parameter_data`` only contains ``values`` information, but other sampling strategies 
   may require extra information to be stored here. An example of this is the usage of ``quantiles`` with Latin 
   Hypercube sampling.
   
   The data variables availble in the ``parameter_study`` object are named according to the 
   ``parameter_set_file_template`` and contain the parameter values unique to each specific parameter set. Examine the 
   contents of the data variables to familiarize yourself with the specific parameter values generated for this 
   particular `Cartesian Product`_ parameter study.

.. admonition:: waves-eabm-tutorial/tutorial_07_cartesian_product/SConscript

   .. literalinclude:: tutorial_07_cartesian_product_SConscript
      :language: Python
      :lineno-match:
      :start-after: marker-3
      :end-before: marker-4

The above code uses the ``set_name`` list of ``Python pathlib`_ objects as an iterable to form the 
``simulation_variables`` parameter substitution dictionary. At first declaration, ``simulation_variables`` is a 
list of parameter values specific to the parameter set ``set_name``. However, recall from 
:ref:`tutorial_parameter_substitution_waves` ref:`tutorial_parameter_substitution_waves_SConscript` that you created a 
:``simulation_variables`` dictionary in the ``SConscript`` file with leading and trailing ``@`` characters for parameter 
substitution. The next line modified the ``simulation_variables`` list and overwrites the variable with a dictionary 
formatted in a way in which you are familiar. The ``parameter_name`` (from iterating on the ``parameter_names`` list) is 
used as the dictionary key padded with leading and trailing ``@`` characters. The value to complete the key-value pair 
is the parameter value from iterating on the previously defined ``simulation_variables`` list. The result is a 
dictionary with keys that can be used for identifying the parameters where the values can be substituted.

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
  the :meth:`waves.builders.copy_substitute` method for SolverPrep. Don't forget to use the leading and trailing ``@`` 
  characters when attempting to access parameter values from the ``simulation_variables`` dictionary.

.. admonition:: waves-eabm-tutorial/tutorial_07_cartesian_product/SConscript

   .. literalinclude:: tutorial_07_cartesian_product_SConscript
      :language: Python
      :lineno-match:
      :start-after: marker-5
      :end-before: marker-6

The code above closes out our familiar workflow with the use of the :meth:`waves.builders.AbaqusSolver` method. Just as 
in previous tutorials, we first run a datacheck to confirm that the Abaqus Solver's requirements are satisfied, and then 
the simulation is executed in ernest. Note that the ``# Abaqus Solver`` code is still within the ``for`` loop, so the 
Abaqus Solver will be called as many times as we have parameter sets. In this case, we will solve four Abaqus 
simulations.

.. admonition:: waves-eabm-tutorial/tutorial_07_cartesian_product/SConscript

   .. literalinclude:: tutorial_07_cartesian_product_SConscript
      :language: Python
      :lineno-match:
      :start-after: marker-6

The final additions to the ``SConscript`` file is a few lines of code that are directly copy-and-pasted from your 
previous tutorial ``SConscript`` file. Note, however, that these final lines of code are outside of the ``for`` loop 
that containted the previous snippets code.

A ``diff`` against the ``SConscript`` file from :ref:`tutorial_include_files_waves` is included below to help identify the
changes made in this tutorial.

.. admonition:: waves-eabm-tutorial/tutorial_07_cartesian_product/SConscript

   .. literalinclude:: tutorial_07_cartesian_product_SConscript
      :language: Python
      :diff: tutorial_06_include_files_SConscript

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

In the commands above, `SCons`_ is instructed to use four threads to build our targets. For this tutorial, four 
``jobs`` is a sensible number, as we have four simulations to run that are independent of each other downstream from 
parameter set generation. By using the ``--jobs=4`` option, `SCons`_ will run all four simulations in parallel.

.. warning::
   
   Be aware of the difference between `SCons`_ thread management and task thread requests. `SCons`_ only manages thread 
   cound (CPU) usage for task execution and does not control multi-threaded tasks. For example, if you specify ``scons 
   --jobs=4``, `SCons`_ will use four worker threaders to execute task action in parallel. If each of the four tasks 
   also specifies multi-threading, `SCons`_ will **not** balance the requested cpu count for each task with the four 
   worker threads already in use. An example of this is using running an Abaqus simulation on multiple CPUs, e.g. 
   ``abaqus_options='-cpus 12'``. In this case, four worker threads that execute tasks each requesting 12 CPUs will 
   result in the consumption of ``4+4*12`` CPUs.

************
Output Files
************

Explore the contents of the ``build`` directory using the ``tree`` command against the ``build`` directory, as shown
below. Note the usage of the ``-I`` to reduce clutter in the ``tree`` command output. The ``-d`` flag specified only 
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
``parameter_set*`` directories will be very similar to that shown for ``parameter_set0``.

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
    ├── single_element_compression_DATACHECK.023
    ├── single_element_compression_DATACHECK.abaqus_v6.env
    ├── single_element_compression_DATACHECK.com
    ├── single_element_compression_DATACHECK.dat
    ├── single_element_compression_DATACHECK.mdl
    ├── single_element_compression_DATACHECK.msg
    ├── single_element_compression_DATACHECK.odb
    ├── single_element_compression_DATACHECK.par
    ├── single_element_compression_DATACHECK.pes
    ├── single_element_compression_DATACHECK.pmg
    ├── single_element_compression_DATACHECK.prt
    ├── single_element_compression_DATACHECK.sim
    ├── single_element_compression_DATACHECK.stdout
    ├── single_element_compression_DATACHECK.stt
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

    0 directories, 50 files

