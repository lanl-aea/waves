.. _tutorial_post_processing_waves:

############################
Tutorial 09: Post-Processing
############################

.. warning::

   The post-processing techniques in this tutorial are a work-in-progress. They should generally work into the future,
   but WAVES may add new behavior to make concatenating results files with the parameter study definition easier. Be sure
   to check back in on this tutorial frequently or watch the :ref:`changelog` for updates!

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

3. Create a directory ``tutorial_09_post_processing`` in the ``waves-eabm-tutorial`` directory.

.. code-block:: bash

   $ pwd
   /path/to/waves-eabm-tutorial
   $ mkdir tutorial_09_post_processing

4. Copy the ``tutorial_08_data_extraction/SConscript`` file into the newly created ``tutorial_09_post_processing``
   directory.

.. code-block:: bash

   $ pwd
   /path/to/waves-eabm-tutorial
   $ cp tutorial_08_data_extraction/SConscript tutorial_09_post_processing/

**********
SConscript
**********

A ``diff`` against the ``SConscript`` file from :ref:`tutorial_include_files_waves` is included below to help identify the
changes made in this tutorial.

.. admonition:: waves-eabm-tutorial/tutorial_09_post_processing/SConscript

   .. literalinclude:: tutorial_09_post_processing_SConscript
      :language: Python
      :diff: tutorial_08_data_extraction_SConscript

**********************
Post-processing script
**********************

5. In the ``waves-eabm-tutorial/eabm_package/python`` directory, create a file called ``plot_scatter.py`` using the
   contents below.

.. admonition:: waves-eabm-tutorial/eabm_package/python/plot_scatter.py

   .. literalinclude:: python_plot_scatter.py
      :language: Python

The script API and CLI are included in the :ref:`sphinx_api`: :ref:`eabm_plot_scatter_api` and :ref:`sphinx_cli`:
:ref:`eabm_plot_scatter_cli`, respectively.

**********
SConstruct
**********

A ``diff`` against the ``SConstruct`` file from :ref:`tutorial_include_files_waves` is included below to help identify the
changes made in this tutorial.

.. admonition:: waves-eabm-tutorial/SConstruct

   .. literalinclude:: eabm_tutorial_09_post_processing_SConstruct
      :language: Python
      :diff: eabm_tutorial_08_data_extraction_SConstruct

*************
Build Targets
*************

6. Build the new targets

.. code-block:: bash

   $ pwd
   /path/to/waves-eabm-tutorial
   $ scons tutorial_09_post_processing --jobs=4

************
Output Files
************
