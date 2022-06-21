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
each. This will result in four total simulations. The parameter sets will look like the following:

.. code-block:: yaml
    
   parameter_set0:
     width: 1
     height: 1
     global_seed: 1
     displacement: -1
   parameter_set1:
     width: 1.1
     height: 1
     global_seed: 1
     displacement: -1
   parameter_set2:
     width: 1
     height: 1.1
     global_seed: 1
     displacement: -1
   parameter_set3:
     width: 1.1
     height: 1.1
     global_seed: 1
     displacement: -1

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

.. admonition:: waves-eabm-tutorial/tutorial_07_cartesian_product/SConscript

   .. literalinclude:: tutorial_07_cartesian_product_SConscript
      :language: Python
      :lineno-match:
      :end-before: marker-1

.. admonition:: waves-eabm-tutorial/tutorial_07_cartesian_product/SConscript

   .. literalinclude:: tutorial_07_cartesian_product_SConscript
      :language: Python
      :lineno-match:
      :start-after: marker-1
      :end-before: marker-2

.. admonition:: waves-eabm-tutorial/tutorial_07_cartesian_product/SConscript

   .. literalinclude:: tutorial_07_cartesian_product_SConscript
      :language: Python
      :lineno-match:
      :start-after: marker-2
      :end-before: marker-3

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

************
Output Files
************
