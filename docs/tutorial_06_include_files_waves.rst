.. _tutorial_include_files_waves:

##########################
Tutorial 06: Include Files
##########################

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

3. Create a directory ``tutorial_06_include_files`` in the ``waves-eabm-tutorial`` directory.

.. code-block:: bash

   $ pwd
   /path/to/waves-eabm-tutorial
   $ mkdir tutorial_06_include_files

4. Copy the ``tutorial_05_parameter_substitution/SConscript`` file into the newly created ``tutorial_06_include_files``
   directory.

.. code-block:: bash

   $ pwd
   /path/to/waves-eabm-tutorial
   $ cp tutorial_05_parameter_substitution/SConscript tutorial_06_include_files/

5. Create a new directory in ``eabm_package/python`` in the ``waves-eabm-tutorial`` directory.

.. code-block:: bash

   $ pwd
   /path/to/waves-eabm-tutorial
   $ mkdir -p eabm_package/python

*********************
Python Parameter File
*********************

In this tutorial, we will update the code from :ref:`tutorial_parameter_substitution_waves` to use an included parameter 
file in favor of hardcoding the parameter definitions in the ``SConscript`` file.

6. Create a new file ``eabm_package/python/single_element_compression_nominal.py`` from the content below.

.. admonition:: waves-eabm-tutorial/eabm_package/python/single_element_compression_nominal.py

   .. literalinclude:: python_single_element_compression_nominal.py 
      :language: Python

The file you just created is an exact copy of the code in your ``tutorial_05_parameter_substitution/SConscript`` file 
that defines the key-value pairs for parameters.

**********
SConscript
**********

7. Use the ``diff`` below to make the following modifications to your ``tutorial_06_include_files/SConscript`` file:

   * Import ``single_element_compression_nominal`` from the ``eabm_package.python`` module
   * Remove the ``simulation_variables`` dictionary that was created in :ref:`tutorial_parameter_substitution_waves`'s 
     code
   * Define ``simulation_variables`` and ``simulation_substituion_dictionary`` using the newly imported 
     ``single_element_compression_nominal`` module

A ``diff`` against the ``SConscript`` file from :ref:`tutorial_parameter_substitution_waves` is included below to help 
identify the changes made in this tutorial.

.. admonition:: waves-eabm-tutorial/tutorial_06_include_files/SConscript

   .. literalinclude:: tutorial_06_include_files_SConscript
      :language: Python
      :diff: tutorial_05_parameter_substitution_SConscript

The first change to be made is importing the ``single_element_compression_nominal`` module from the 
``eabm_package.python`` module you created in the previous tutorial step. This import statement will import all 
variables within the ``single_element_compression_nominal.py`` file and make them available in the ``SConscript`` file's 
name space. See the `Python Modules`_ documentation for more information about importing modules. You can access those 
variables with the following syntax:

.. code-block:: python

   single_element_compression_nominal.simulation_variables
   single_element_compression_nominal.simulation_substitution_dictionary

The second change removes the code that defines ``simulation_variables`` and ``simulation_substitution_dictionary`` that 
remained from :ref:`tutorial_parameter_substitution_waves`'s code.

The final change made in the ``tutorial_06_include_files/SConscript`` file is to re-define the ``simulation_variables`` 
and ``simulation_substitution_dictionary`` variables by utlizing the ``single_element_compression_nominal`` module. The 
The end result at this point in the code is the same between this tutorial and 
:ref:`tutorial_parameter_substitution_waves`. However, now we import variables from a separate file, and allow ourselves
the ability to change parameters without modification to the ``SConscript`` file.

**********
SConstruct
**********

8. Use the ``diff`` below to modify your ``waves-eabm-tutorial/SConstruct file`` in the following ways:
   
   * Add the ``waves-eabm-tutorial`` directory to your PYTHONPATH to make the ``eabm_package`` importable
   * Add the ``python_source_dir`` key-value pair to the ``project_variables`` dictionary
   * Add ``tutorial_06_include_files`` to the ``eabm_simulation_directories`` list

A ``diff`` against the ``SConstruct`` file from :ref:`tutorial_parameter_substitution_waves` is included below to help identify the
changes made in this tutorial.

.. admonition:: waves-eabm-tutorial/SConstruct

   .. literalinclude:: eabm_tutorial_06_include_files_SConstruct
      :language: Python
      :diff: eabm_tutorial_05_parameter_substitution_SConstruct

The first change you made allows for us to import modules from the ``eabm_package`` package. This step is neccessary to 
be able to import the ``eabm_package.python`` module in the ``tutorial_06_include_files/SConscript`` file.

The next c

*************
Build Targets 
*************

7. Build the new targets

.. code-block:: bash

   $ pwd
   /path/to/waves-eabm-tutorial
   $ scons tutorial_06_include_files

************
Output Files
************
