.. _tutorial_sensitivity_study:

###########################
Tutorial: Sensitivity Study
###########################

.. include:: wip_warning.txt

**********
References
**********

* `numpy.corrcoef`_ :cite:`numpy`
* `SALib.analyze`_ :cite:`salib`
* `seaborn.pairplot`_ :cite:`seaborn`

***********
Environment
***********

.. include:: tutorial_environment_activation.txt

.. include:: version_check_warning.txt

*******************
Directory Structure
*******************

.. include:: tutorial_directory_setup.txt

.. note::

    If you skipped any of the previous tutorials, run the following commands to create a copy of the necessary tutorial
    files.

    .. code-block:: bash

        $ pwd
        /home/roppenheimer/waves-tutorials
        $ waves fetch --overwrite --destination modsim_package tutorials/modsim_package/__init__.py
        WAVES fetch
        Destination directory: 'modsim_package'
        $ waves fetch --overwrite --destination modsim_package/abaqus 'tutorials/modsim_package/abaqus/*'
        WAVES fetch
        Destination directory: 'modsim_package/abaqus'
        $ waves fetch --overwrite --destination modsim_package/python 'tutorials/modsim_package/python/__init__.py' 'tutorials/modsim_package/python/rectangle_compression_nominal.py' 'tutorials/modsim_package/python/rectangle_compression_cartesian_product.py' 'tutorials/modsim_package/python/post_processing.py'
        WAVES fetch
        Destination directory: 'modsim_package/python'
        $ waves fetch --overwrite 'tutorials/tutorial_01_geometry' 'tutorials/tutorial_02_partition_mesh' 'tutorials/tutorial_03_solverprep' 'tutorials/tutorial_04_simulation' 'tutorials/tutorial_05_parameter_substitution' 'tutorials/tutorial_06_include_files' 'tutorials/tutorial_07_cartesian_product' 'tutorials/tutorial_08_data_extraction' 'tutorials/tutorial_09_post_processing'
        WAVES fetch
        Destination directory: '/home/roppenheimer/waves-tutorials'
        $ waves fetch tutorials/tutorial_09_post_processing_SConstruct && mv tutorial_09_post_processing_SConstruct SConstruct
        WAVES fetch
        Destination directory: '/home/roppenheimer/waves-tutorials'

4. Download and copy the ``tutorial_09_post_processing`` file to a new file named ``tutorial_sensitivity_study``
   with the :ref:`waves_cli` :ref:`waves_fetch_cli` subcommand.

.. code-block:: bash

   $ pwd
   /home/roppenheimer/waves-tutorials
   $ waves fetch --overwrite tutorials/tutorial_09_post_processing && cp tutorial_09_post_processing tutorial_sensitivity_study
   WAVES fetch
   Destination directory: '/home/roppenheimer/waves-tutorials'

**********
SConscript
**********

A ``diff`` against the ``tutorial_09_post_processing`` file from :ref:`tutorial_post_processing` is included below to
help identify the changes made in this tutorial.

.. admonition:: waves-tutorials/tutorial_sensitivity_study

   .. literalinclude:: tutorials_tutorial_sensitivity_study
      :language: Python
      :diff: tutorials_tutorial_09_post_processing

**********************
Post-processing script
**********************

5. In the ``waves-tutorials/modsim_package/python`` directory, create a file called ``sensitivity_study.py`` using the
   contents below.

.. admonition:: waves-tutorials/modsim_package/python/sensitivity_study.py

   .. literalinclude:: python_sensitivity_study.py
      :language: Python

A ``diff`` against the ``post_processing.py`` file from :ref:`tutorial_post_processing` is included below to
help identify the changes made in this tutorial.

.. admonition:: waves-tutorials/modsim_package/python/sensitivity_study.py

   .. literalinclude:: python_sensitivity_study.py
      :language: Python
      :diff: python_post_processing.py

**********
SConstruct
**********

6. Update the ``SConstruct`` file. A ``diff`` against the ``SConstruct`` file from :ref:`tutorial_post_processing`
   is included below to help identify the changes made in this tutorial.

.. admonition:: waves-tutorials/SConstruct

   .. literalinclude:: tutorials_tutorial_sensitivity_study_SConstruct
      :language: Python
      :diff: tutorials_tutorial_09_post_processing_SConstruct

*************
Build Targets
*************

7. Build the new sensitivity study targets

.. code-block:: bash

   $ pwd
   /home/roppenheimer/waves-tutorials
   $ scons tutorial_sensitivity_study --jobs=4
   <output truncated>

************
Output Files
************

Explore the contents of the ``build`` directory using the ``tree`` command against the ``build`` directory, as shown
below. Note that the output files from the previous tutorials may also exist in the ``build`` directory, but the
directory is specified by name to reduce clutter in the output shown.

.. code-block:: bash

   $ pwd
   /home/roppenheimer/waves-tutorials
   $ tree build/tutorial_sensitivity_study
