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

In this tutorial, we will update the code from :ref:`tutorial_parameter_substitution` to use an included parameter file 
in favor of hardcoding the parameter definitions in the ``SConscript`` file.

6. Create a new file ``eabm_package/python/single_element_compression_nominal.py`` from the content below.

.. admonition:: waves-eabm-tutorial/eabm_package/python/single_element_compression_nominal.py

   .. literalinclude:: python_single_element_compression_nominal.py 
      :language: Python

The file you just created is an exact copy of the code in your ``tutorial_05_parameter_substitution/SConscript`` file 
that defines the key-value pairs for parameters.

**********
SConscript
**********

A ``diff`` against the ``SConscript`` file from :ref:`tutorial_parameter_substitution_waves` is included below to help identify the
changes made in this tutorial.

.. admonition:: waves-eabm-tutorial/tutorial_06_include_files/SConscript

   .. literalinclude:: tutorial_06_include_files_SConscript
      :language: Python
      :diff: tutorial_05_parameter_substitution_SConscript

**********
SConstruct
**********

A ``diff`` against the ``SConstruct`` file from :ref:`tutorial_parameter_substitution_waves` is included below to help identify the
changes made in this tutorial.

.. admonition:: waves-eabm-tutorial/SConstruct

   .. literalinclude:: eabm_tutorial_06_include_files_SConstruct
      :language: Python
      :diff: eabm_tutorial_05_parameter_substitution_SConstruct

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
