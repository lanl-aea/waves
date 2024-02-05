.. _tutorial_unit_testing_waves:

######################
Tutorial: Unit Testing
######################

.. include:: wip_warning.txt

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

.. include:: tutorial_directory_setup.txt

.. note::

    If you skipped any of the previous tutorials, run the following commands to create a copy of the necessary tutorial
    files.

    .. code-block:: bash

        $ pwd
        /home/roppenheimer/waves-tutorials
        $ waves fetch --overwrite --destination eabm_package tutorials/eabm_package/__init__.py
        WAVES fetch
        Destination directory: 'eabm_package'
        $ waves fetch --overwrite --destination eabm_package/abaqus 'tutorials/eabm_package/abaqus/*'
        WAVES fetch
        Destination directory: 'eabm_package/abaqus'
        $ waves fetch --overwrite --destination eabm_package/python 'tutorials/eabm_package/python/__init__.py' 'tutorials/eabm_package/python/rectangle_compression_nominal.py' 'tutorials/eabm_package/python/rectangle_compression_cartesian_product.py' 'tutorials/eabm_package/python/post_processing.py'
        WAVES fetch
        Destination directory: 'eabm_package/python'
        $ waves fetch tutorials/tutorial_09_post_processing_SConstruct && mv tutorial_09_post_processing_SConstruct SConstruct
        WAVES fetch
        Destination directory: '/home/roppenheimer/waves-tutorials'

4. Download and copy the ``tutorial_09_post_processing`` file to a new file named ``tutorial_unit_testing``
   with the :ref:`waves_cli` :ref:`waves_fetch_cli` subcommand.

.. code-block:: bash

   $ pwd
   /home/roppenheimer/waves-tutorials
   $ waves fetch --overwrite tutorials/tutorial_09_post_processing && cp tutorial_09_post_processing tutorial_unit_testing
   WAVES fetch
   Destination directory: '/home/roppenheimer/waves-tutorials'

.. _tutorials_tutorial_unit_testing_waves:

**********
SConscript
**********

A ``diff`` against the ``tutorial_09_post_processing`` file from :ref:`tutorial_post_processing_waves` is included below to help identify the
changes made in this tutorial.

.. admonition:: waves-tutorials/tutorial_unit_testing

   .. literalinclude:: tutorials_tutorial_unit_testing
      :language: Python
      :diff: tutorials_tutorial_09_post_processing

**********
SConstruct
**********

A ``diff`` against the ``SConstruct`` file from :ref:`tutorial_post_processing_waves` is included below to help identify the
changes made in this tutorial.

.. admonition:: waves-tutorials/SConstruct

   .. literalinclude:: tutorials_tutorial_unit_testing_SConstruct
      :language: Python
      :diff: tutorials_tutorial_09_post_processing_SConstruct

*************
Build Targets
*************

5. Build the new targets

.. code-block:: bash

   $ pwd
   /home/roppenheimer/waves-tutorials
   $ scons tutorial_unit_testing

************
Output Files
************

Explore the contents of the ``build`` directory using the ``tree`` command against the ``build`` directory, as shown
below. Note that the output files from the previous tutorials also exist in the ``build`` directory, but the directory
is specified by name to reduce clutter in the output shown.

.. code-block:: bash

   $ pwd
   /home/roppenheimer/waves-tutorials
   $ tree build/tutorial_unit_testing/
