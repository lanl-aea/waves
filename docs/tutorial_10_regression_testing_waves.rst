.. _tutorial_regression_testing_waves:

###############################
Tutorial 10: Regression Testing
###############################

**********
References
**********

* Gitlab CI: https://docs.gitlab.com/ee/ci/ :cite:`gitlab-ci`

***********
Environment
***********

.. include:: tutorial_environment_activation.txt

*******************
Directory Structure
*******************

3. Create a directory ``tutorial_10_regression_testing`` in the ``waves-eabm-tutorial`` directory.

.. code-block:: bash

   $ pwd
   /path/to/waves-eabm-tutorial
   $ mkdir tutorial_10_regression_testing

4. Copy the ``tutorial_09_post_processing/SConscript`` file into the newly created ``tutorial_10_regression_testing``
   directory.

.. code-block:: bash

   $ pwd
   /path/to/waves-eabm-tutorial
   $ cp tutorial_09_post_processing/SConscript tutorial_10_regression_testing/

**********
SConscript
**********

A ``diff`` against the ``SConscript`` file from :ref:`tutorial_post_processing_waves` is included below to help identify the
changes made in this tutorial.

.. admonition:: waves-eabm-tutorial/tutorial_10_regression_testing/SConscript

   .. literalinclude:: tutorial_10_regression_testing_SConscript
      :language: Python
      :diff: tutorial_09_post_processing_SConscript

**********
SConstruct
**********

A ``diff`` against the ``SConstruct`` file from :ref:`tutorial_include_files_waves` is included below to help identify the
changes made in this tutorial.

.. admonition:: waves-eabm-tutorial/SConstruct

   .. literalinclude:: eabm_tutorial_10_regression_testing_SConstruct
      :language: Python
      :diff: eabm_tutorial_09_post_processing_SConstruct

*************
Build Targets
*************

6. Build the new targets

.. code-block:: bash

   $ pwd
   /path/to/waves-eabm-tutorial
   $ scons datacheck --jobs=4

************
Output Files
************
