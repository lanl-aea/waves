.. _tutorial_extend_study:

#########################################
Automatically Extending a Parameter Study
#########################################

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

   .. only:: not epub

      .. tab-set::
         :sync-group: OS

         .. tab-item:: Linux/MacOS
            :sync: bash

            .. code-block::

               $ pwd
               /home/roppenheimer/waves-tutorials
               $ waves fetch --overwrite --tutorial 8 && mv tutorial_08_data_extraction_SConstruct SConstruct
               WAVES fetch
               Destination directory: '/home/roppenheimer/waves-tutorials'

         .. tab-item:: Windows
            :sync: powershell

            .. code-block::

               PS > Get-Location

               Path
               ----
               C:\Users\roppenheimer\waves-tutorials

               PS > waves fetch --overwrite --tutorial 8 && Move-Item tutorial_08_data_extraction_SConstruct SConstruct -Force
               WAVES fetch
               Destination directory: 'C:\Users\roppenheimer\waves-tutorials'

4. Download and copy the ``tutorial_08_data_extraction.scons`` file to a new file named ``tutorial_extend_study.scons``
   with the :ref:`waves_cli` :ref:`waves_fetch_cli` subcommand.

.. only:: not epub

   .. tab-set::
      :sync-group: OS

      .. tab-item:: Linux/MacOS
         :sync: bash

         .. code-block:: bash

            $ pwd
            /home/roppenheimer/waves-tutorials
            $ waves fetch --overwrite tutorials/tutorial_08_data_extraction.scons && cp tutorial_08_data_extraction.scons tutorial_extend_study.scons
            WAVES fetch
            Destination directory: '/home/roppenheimer/waves-tutorials'

      .. tab-item:: Windows
         :sync: powershell

         .. code-block:: powershell

            PS > Get-Location

            Path
            ----
            C:\Users\roppenheimer\waves-tutorials

            PS > waves fetch --overwrite tutorials\tutorial_08_data_extraction.scons && Copy-Item tutorial_08_data_extraction.scons tutorial_extend_study.scons
            WAVES fetch
            Destination directory: 'C:\Users\roppenheimer\waves-tutorials'

**********
SConscript
**********

A ``diff`` against the ``tutorial_08_data_extraction.scons`` file from :ref:`tutorial_data_extraction` is included below
to help identify the differences between the two parameter generators and workflows.

.. admonition:: waves-tutorials/tutorial_extend_study.scons

   .. literalinclude:: tutorials_tutorial_extend_study.scons
      :language: Python
      :diff: tutorials_tutorial_08_data_extraction.scons

This post-processing workflow should look nearly identical to the post-processing tasks introduced in
:ref:`tutorial_post_processing`. The difference in this tutorial is that there are two parameter study files to track.
The configuration time parameter study is written to ``parameter_study.h5`` as before, but the
``previous_parameter_study`` now reads from a new file, ``extended_parameter_study.h5``, which does not exist until the
workflow is run at least once.

A post-processing task is written to generate the ``extended_parameter_study.h5`` as a final step of the workflow. As
shown in the next section where the post-processing file is introduced, this task reads the ``parameter_study.h5`` file
and the associated simulation results, performs some analysis, and either writes new parameter sets into the
``extended_parameter_study.h5`` file or simply creates a copy of the ``parameter_study.h5`` file. Because the
configuration time parameter study reads from ``extended_parameter_study.h5``, the next time the workflow is executed,
it will pick up any new parameter sets and configure the new sets as part of the workflow. This process of performing
new work continues until the the post-processing task no longer recommends new parameter sets.

Both the configuration time parameter study definition found in the ``SConscript`` file and the post-processing
parameter study extension take advantage of the WAVES feature that preserves set name assignments of the original
parameter sets. At each re-execution of the workflow, parameter sets that have already been seen preserve their original
set names and set contents. Those set-named output files already exist, so re-work is minimized to the newest parameter
sets.

The WAVES :ref:`waves_build_cli` subcommand was written to help automate the process of re-execution. The command is
written to continue re-submitting the normal ``scons`` command until `SCons`_ reports that there is no new work to
complete, as when the post-processing script no longer recommends new parameter sets, or until the maximum number of
iterations has been reached.

**********************
Post-processing script
**********************

5. In the ``waves-tutorials/modsim_package/python`` directory, create a file called ``tutorial_extend_study.py`` using
   the contents below.

.. admonition:: waves-tutorials/modsim_package/python/tutorial_extend_study.py

   .. literalinclude:: python_tutorial_extend_study.py
      :language: Python

This post-processing script is a stripped down version of the ``post_processing.py`` script introduced in
:ref:`tutorial_post_processing`. The ``tutorial_extend_study.py`` script simply checks the number of simulations and
increases the size of the parameter study to a hardcoded value. This simple implementation is intended only to
demonstrate the workflow and task structure of an automatically extending workflow.

In real projects, the purpose of extending a parameter is to perform an optimization or uncertainty quantification
workflow. A post-processing script more similar to the ``post_processing.py`` script of :ref:`tutorial_post_processing`
or :ref:`tutorial_sensitivity_study` would perform some kind of sensitivity analysis or uncertainty quantification and
recommend new parameter sets to meet an objective function. Such a workflow may also require several post-processing
steps, such as training a reduced-order or surrogate model which is used to investigate a larger parameter space before
recommending parameter sets to investigate with the original, higher cost simulations.

In all these examples, the outcome of the post-processing step should be new parameter sets that are added to the
original parameter study. On re-execution of the workflow, the new parameter sets are read into the workflow definition
and the workflow picks up with the new parameter sets without re-computing the old ones.

**********
SConstruct
**********

A ``diff`` against the ``SConstruct`` file from :ref:`tutorial_data_extraction` is included below to help identify the
changes made in this tutorial.

.. admonition:: waves-tutorials/SConstruct

   .. literalinclude:: tutorials_tutorial_extend_study_SConstruct
      :language: Python
      :diff: tutorials_tutorial_08_data_extraction_SConstruct

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
