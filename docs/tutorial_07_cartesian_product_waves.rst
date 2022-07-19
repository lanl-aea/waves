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
      :emphasize-lines: 8, 11

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
      :emphasize-lines: 6-10

The unhighlighted portions of the code snippet above do not present any unique code that has not been previously 
discussed.

The highlighted portions of the code snippet above define some new ``simulation_variables`` for this tutorial. The 
``current_build_directory`` is the absolute path of the directory where the ``SConscript`` lives and is constructed as a 
`Python pathlib`_ object.

.. admonition:: waves-eabm-tutorial/tutorial_07_cartesian_product/SConscript

   .. literalinclude:: tutorial_07_cartesian_product_SConscript
      :language: Python
      :lineno-match:
      :start-after: marker-2
      :end-before: marker-3

.. admonition:: waves-eabm-tutorial/tutorial_07_cartesian_product/examine_parameter_study_object.py
   
   .. literalinclude:: tutorial_07_cartesian_product_examine_parameter_study_object.py
      :language: Python
      :lineno-match:

.. literalinclude:: tutorial_07_cartesian_product_parameter_study_message.txt


.. admonition:: waves-eabm-tutorial/tutorial_07_cartesian_product/SConscript

   .. literalinclude:: tutorial_07_cartesian_product_SConscript
      :language: Python
      :lineno-match:
      :start-after: marker-3
      :end-before: marker-4

.. admonition:: waves-eabm-tutorial/tutorial_07_cartesian_product/SConscript

   .. literalinclude:: tutorial_07_cartesian_product_SConscript
      :language: Python
      :lineno-match:
      :start-after: marker-4
      :end-before: marker-5

.. admonition:: waves-eabm-tutorial/tutorial_07_cartesian_product/SConscript

   .. literalinclude:: tutorial_07_cartesian_product_SConscript
      :language: Python
      :lineno-match:
      :start-after: marker-5
      :end-before: marker-6

.. admonition:: waves-eabm-tutorial/tutorial_07_cartesian_product/SConscript

   .. literalinclude:: tutorial_07_cartesian_product_SConscript
      :language: Python
      :lineno-match:
      :start-after: marker-6
      :end-before: marker-7

.. admonition:: waves-eabm-tutorial/tutorial_07_cartesian_product/SConscript

   .. literalinclude:: tutorial_07_cartesian_product_SConscript
      :language: Python
      :lineno-match:
      :start-after: marker-7

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

