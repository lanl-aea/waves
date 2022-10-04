.. _tutorial_remote_execution_waves:

############################
Tutorial: Simulation via SSH
############################

This tutorial implements the same workflow introduced in :ref:`tutorial_simulation_waves`, but executes the simulation
on a remote server via SSH.

**********
References
**********

* SCons Tar builder
* ``ssh``
* ``rsync``
* ``tar``

***********
Environment
***********

.. include:: tutorial_environment_activation.txt

*******************
Directory Structure
*******************

3. Create directories ``tutorial_remote_execution`` and ``eabm_package/cubit`` in the ``waves-eabm-tutorial`` directory.

.. code-block:: bash

   $ pwd
   /path/to/waves-eabm-tutorial
   $ mkdir -p tutorial_remote_execution

4. Copy the ``tutorial_04_simulation/SConscript`` file into the newly created ``tutorial_remote_execution``
   directory.

.. code-block:: bash

   $ pwd
   /path/to/waves-eabm-tutorial
   $ cp tutorial_04_simulation/SConscript tutorial_remote_execution/

.. _tutorial_remote_execution_waves_SConscript:

**********
SConscript
**********

A ``diff`` against the ``SConscript`` file from :ref:`tutorial_simulation_waves` is included below to help identify the
changes made in this tutorial.

.. admonition:: waves-eabm-tutorial/tutorial_remote_execution/SConscript

   .. literalinclude:: tutorial_remote_execution_SConscript
      :language: Python
      :diff: tutorial_04_simulation_SConscript

Note that Cubit does not support the Abaqus plane stress element ``CPS4``, so we must add a post-action to the orphan
mesh target to change the element type. A post-action is used to avoid generating intermediate target files, which would
be required if we created a separate task for the file modification. This post-action is written to apply to a list, so
if additional orphan mesh files needed the same modification, the post-action would be added to each targets' build
signature definition with a single ``AddPostAction`` definition.

The ``sed`` command is not available on all systems, but a `Conda`_ packaged version, `conda-forge sed`_, of the `GNU
sed`_ program can be used to provide system-to-system consistency with `Conda environment management`_. See the `Conda`_
documentation for more information about virtual environment management with `Conda`_.

*******************
Cubit Journal Files
*******************

5. Create the following journal files in the ``waves-eabm-tutorial/eabm_package/cubit`` directory.

The Cubit journal files include the same CLI introduced in :ref:`tutorial_partition_mesh_waves` for the Abaqus journal
files. Besides the differences in Abaqus and Cubit commands, the major difference between the Abaqus and Cubit journal
files is the opportunity to use Python 3 with Cubit, where Abaqus journal files must use the Abaqus controlled
installation of Python 2. The API and CLI built from the Cubit journal files' docstrings may be found in the
:ref:`waves_eabm_api` for :ref:`cubit_journal_api` and the :ref:`waves_eabm_cli` for :ref:`cubit_journal_cli`,
respectively.

.. admonition:: waves-eabm-tutorial/eabm_package/cubit/single_element_geometry.py

   .. literalinclude:: cubit_single_element_geometry.py
       :language: Python
       :lineno-match:

.. admonition:: waves-eabm-tutorial/eabm_package/cubit/single_element_partition.py

   .. literalinclude:: cubit_single_element_partition.py
       :language: Python
       :lineno-match:

.. admonition:: waves-eabm-tutorial/eabm_package/cubit/single_element_mesh.py

   .. literalinclude:: cubit_single_element_mesh.py
       :language: Python
       :lineno-match:

**********
SConstruct
**********

A ``diff`` against the ``SConstruct`` file from :ref:`tutorial_simulation_waves` is included below to help identify the
changes made in this tutorial.

.. admonition:: waves-eabm-tutorial/SConstruct

   .. literalinclude:: tutorials_tutorial_remote_execution_SConstruct
      :language: Python
      :diff: tutorials_tutorial_04_simulation_SConstruct

*************
Build Targets
*************

6. Build the new targets

.. code-block:: bash

   $ pwd
   /path/to/waves-eabm-tutorial
   $ scons tutorial_remote_execution

************
Output Files
************

Explore the contents of the ``build`` directory using the ``tree`` command against the ``build`` directory, as shown
below. Note that the output files from the previous tutorials also exist in the ``build`` directory, but the directory
is specified by name to reduce clutter in the ouptut shown.

.. code-block:: bash

   $ pwd
   /home/roppenheimer/waves-eabm-tutorial
   $ tree build/tutorial_remote_execution/
