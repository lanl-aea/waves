.. _tutorial_extend_study:

#########################################
Automatically Extending a Parameter Study
#########################################

.. warning::

   The ``waves build`` feature is considered experimental. The feature should be treated like an alpha feature whose
   design, behavior, and interface may change without notice. This feature is documented to solicit user feedback on
   preferred behavior and usefulness.

.. include:: wip_warning.txt

**********
References
**********

* :ref:`waves_cli` :ref:`waves_build_cli` subcommand
* |PROJECT| :ref:`parameter_generator_api` API: :meth:`waves.parameter_generators.SobolSequence`
* `Xarray`_ and the `xarray dataset`_ :cite:`xarray,hoyer2017xarray`

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
        $ waves fetch --overwrite --tutorial 7
        WAVES fetch
        Destination directory: '/home/roppenheimer/waves-tutorials'
        $ waves fetch --overwrite 'tutorials/tutorial_07_sobol_sequence_SConstruct' 'tutorials/modsim_package/python/rectangle_compression_sobol_sequence.py' && mv tutorial_07_sobol_sequence_SConstruct SConstruct
        WAVES fetch
        Destination directory: '/home/roppenheimer/waves-tutorials'

4. Download and copy the ``tutorial_07_sobol_sequence`` file to a new file named ``tutorial_extend_study``
   with the :ref:`waves_cli` :ref:`waves_fetch_cli` subcommand.

.. code-block:: bash

   $ pwd
   /home/roppenheimer/waves-tutorials
   $ waves fetch --overwrite tutorials/tutorial_07_sobol_sequence && cp tutorial_07_sobol_sequence tutorial_extend_study
   WAVES fetch
   Destination directory: '/home/roppenheimer/waves-tutorials'

**********
SConscript
**********

A ``diff`` against the ``tutorial_07_sobol_sequence`` file from :ref:`tutorial_sobol_sequence` is included below to help identify the
differences between the two parameter generators.

.. admonition:: waves-tutorials/tutorial_extend_study

   .. literalinclude:: tutorials_tutorial_extend_study
      :language: Python
      :diff: tutorials_tutorial_07_sobol_sequence

**********
SConstruct
**********

A ``diff`` against the ``SConstruct`` file from :ref:`tutorial_sobol_sequence` is included below to help identify the
changes made in this tutorial.

.. admonition:: waves-tutorials/SConstruct

   .. literalinclude:: tutorials_tutorial_extend_study_SConstruct
      :language: Python
      :diff: tutorials_tutorial_07_sobol_sequence_SConstruct

*************
Build Targets
*************

5. Build the new targets

.. code-block:: bash

   $ pwd
   /home/roppenheimer/waves-tutorials
   $ waves build --max-iterations=4 tutorial_extend_study --jobs=4

************
Output Files
************

.. code-block:: bash

   $ pwd
   /home/roppenheimer/waves-tutorials
   $ tree build/tutorial_extend_study -d
   build/tutorial_extend_study
   |-- parameter_set0
   |-- parameter_set1
   |-- parameter_set2
   |-- parameter_set3
   |-- parameter_set4
   |-- parameter_set5
   |-- parameter_set6
   `-- parameter_set7

   8 directories
