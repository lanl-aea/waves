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

3. Create directory``tutorial_remote_execution`` in the ``waves-eabm-tutorial`` directory.

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
