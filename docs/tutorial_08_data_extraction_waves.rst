.. _tutorial_data_extraction_waves:

############################
Tutorial 08: Data Extraction
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

3. Create a directory ``tutorial_08_data_extraction`` in the ``waves-eabm-tutorial`` directory.

.. code-block:: bash

   $ pwd
   /path/to/waves-eabm-tutorial
   $ mkdir tutorial_08_data_extraction

4. Copy the ``tutorial_07_cartesian_product/SConscript`` file into the newly created ``tutorial_08_data_extraction``
   directory.

.. code-block:: bash

   $ pwd
   /path/to/waves-eabm-tutorial
   $ cp tutorial_07_cartesian_product/SConscript tutorial_08_data_extraction/

**********
SConscript
**********

A ``diff`` against the ``SConscript`` file from :ref:`tutorial_cartesian_product_waves` is included below to help identify the
changes made in this tutorial.

.. admonition:: waves-eabm-tutorial/tutorial_08_data_extraction/SConscript

   .. literalinclude:: tutorial_08_data_extraction_SConscript
      :language: Python
      :diff: tutorial_07_cartesian_product_SConscript

**********
SConstruct
**********

A ``diff`` against the ``SConstruct`` file from :ref:`tutorial_cartesian_product_waves` is included below to help identify the
changes made in this tutorial.

.. admonition:: waves-eabm-tutorial/SConstruct

   .. literalinclude:: eabm_tutorial_08_data_extraction_SConstruct
      :language: Python
      :diff: eabm_tutorial_07_cartesian_product_SConstruct

*************
Build Targets
*************

5. Build the new targets

.. code-block:: bash

   $ pwd
   /path/to/waves-eabm-tutorial
   $ scons tutorial_08_data_extraction --jobs=4

************
Output Files
************
