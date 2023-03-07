.. _tutorial_remote_execution_waves:

############################
Tutorial: Simulation via SSH
############################

.. include:: wip_warning.txt

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

3. Copy the ``tutorial_04_simulation`` file to a new file named ``tutorial_remote_execution``

.. code-block:: bash

   $ pwd
   /path/to/waves-tutorials
   $ cp tutorial_04_simulation tutorial_remote_execution

.. _tutorials_tutorial_remote_execution_waves:

**********
SConscript
**********

A ``diff`` against the ``tutorial_04_simulation`` file from :ref:`tutorial_simulation_waves` is included below to help identify the
changes made in this tutorial.

.. admonition:: waves-tutorials/tutorial_remote_execution

   .. literalinclude:: tutorials_tutorial_remote_execution
      :language: Python
      :diff: tutorials_tutorial_04_simulation

**********
SConstruct
**********

A ``diff`` against the ``SConstruct`` file from :ref:`tutorial_simulation_waves` is included below to help identify the
changes made in this tutorial.

.. admonition:: waves-tutorials/SConstruct

   .. literalinclude:: tutorials_tutorial_remote_execution_SConstruct
      :language: Python
      :diff: tutorials_tutorial_04_simulation_SConstruct

*************
Build Targets
*************

4. Build the new targets

.. code-block:: bash

   $ pwd
   /path/to/waves-tutorials
   $ scons tutorial_remote_execution

************
Output Files
************

Explore the contents of the ``build`` directory using the ``tree`` command against the ``build`` directory, as shown
below. Note that the output files from the previous tutorials also exist in the ``build`` directory, but the directory
is specified by name to reduce clutter in the ouptut shown.

.. code-block:: bash

   $ pwd
   /home/roppenheimer/waves-tutorials
   $ tree build/tutorial_remote_execution/
