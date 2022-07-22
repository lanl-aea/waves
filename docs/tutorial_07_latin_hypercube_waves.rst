.. _tutorial_latin_hypercube_waves:

############################
Tutorial 07: Latin Hypercube
############################

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

3. Create a directory ``tutorial_07_latin_hypercube`` in the ``waves-eabm-tutorial`` directory.

.. code-block:: bash

   $ pwd
   /path/to/waves-eabm-tutorial
   $ mkdir tutorial_07_latin_hypercube

4. Copy the ``tutorial_06_include_files/SConscript`` file into the newly created ``tutorial_07_latin_hypercube``
   directory.

.. code-block:: bash

   $ pwd
   /path/to/waves-eabm-tutorial
   $ cp tutorial_06_include_files/SConscript tutorial_07_latin_hypercube/

********************
Parameter Study File
********************

5. Create a new file ``eabm_package/python/tutorial_07_latin_hypercube.py`` from the content below.

.. admonition:: waves-eabm-tutorial/eabm_package/python/tutorial_07_latin_hypercube.py

   .. literalinclude:: python_tutorial_07_latin_hypercube.py
      :language: Python

**********
SConscript
**********

The ``diff`` for changes in the ``SConscript`` file for this tutorial is extensive because of the for loop indent
wrapping the task generation for each parameter set. For convenience, the full source file is included below to aid in a
wholesale copy and paste when creating the new ``SConscript`` file.

.. admonition:: waves-eabm-tutorial/tutorial_07_latin_hypercube/SConscript

   .. literalinclude:: tutorial_07_latin_hypercube_SConscript
      :language: Python

A ``diff`` against the ``SConscript`` file from :ref:`tutorial_cartesian_product_waves` is included below to help identify the
differences between the two parameter generators.

.. admonition:: waves-eabm-tutorial/tutorial_07_latin_hypercube/SConscript

   .. literalinclude:: tutorial_07_latin_hypercube_SConscript
      :language: Python
      :diff: tutorial_07_cartesian_product_SConscript

**********
SConstruct
**********

A ``diff`` against the ``SConstruct`` file from :ref:`tutorial_include_files_waves` is included below to help identify the
changes made in this tutorial.

.. admonition:: waves-eabm-tutorial/SConstruct

   .. literalinclude:: eabm_tutorial_07_latin_hypercube_SConstruct
      :language: Python
      :diff: eabm_tutorial_06_include_files_SConstruct

*************
Build Targets
*************

6. Build the new targets

.. code-block:: bash

   $ pwd
   /path/to/waves-eabm-tutorial
   $ scons tutorial_07_latin_hypercube --jobs=4

************
Output Files
************
