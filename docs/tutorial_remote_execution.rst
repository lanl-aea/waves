.. _tutorial_remote_execution:

############################
Tutorial: Simulation via SSH
############################

.. include:: wip_warning.txt

.. include:: ssh_builder_actions_warning.txt

This tutorial implements the same workflow introduced in :ref:`tutorial_simulation`, but executes the simulation
on a remote server via SSH. You may need to update the server name to match your local system or local remote server.

This tutorial assumes that the local system has an installation of Abaqus and that the Abaqus installation on the local
system is indentical to the installation on the remote server. You may need to update both Abaqus paths to match the
respective systems.

**********
References
**********

* ``ssh``
* ``rsync``

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
        $ waves fetch --overwrite --tutorial 4 && mv tutorial_04_simulation_SConstruct SConstruct
        Destination directory: '/home/roppenheimer/waves-tutorials'

4. Download and copy the ``tutorial_04_simulation`` file to a new file named ``tutorial_remote_execution``
   with the :ref:`waves_cli` :ref:`waves_fetch_cli` subcommand.

.. code-block:: bash

   $ pwd
   /home/roppenheimer/waves-tutorials
   $ waves fetch --overwrite tutorials/tutorial_04_simulation && cp tutorial_04_simulation tutorial_remote_execution
   WAVES fetch
   Destination directory: '/home/roppenheimer/waves-tutorials'

.. _tutorials_tutorial_remote_execution:

**********
SConscript
**********

A ``diff`` against the ``tutorial_04_simulation`` file from :ref:`tutorial_simulation` is included below to help identify the
changes made in this tutorial.

.. admonition:: waves-tutorials/tutorial_remote_execution

   .. literalinclude:: tutorials_tutorial_remote_execution
      :language: Python
      :diff: tutorials_tutorial_04_simulation

**********
SConstruct
**********

A ``diff`` against the ``SConstruct`` file from :ref:`tutorial_simulation` is included below to help identify the
changes made in this tutorial.

.. admonition:: waves-tutorials/SConstruct

   .. literalinclude:: tutorials_tutorial_remote_execution_SConstruct
      :language: Python
      :diff: tutorials_tutorial_04_simulation_SConstruct

*************
Build Targets
*************

5. Build the new targets

.. code-block:: bash

   $ pwd
   /home/roppenheimer/waves-tutorials
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
