.. _tutorial_pseudo_variables_waves:

##########################
Tutorial: Pseudo Variables
##########################

In addition to source and target file signatures, SCons saves a build signature that includes information about the
action required to build the target. The build signature will include the substitution variables used in the task. For
example, the contents of the ``abaqus_options`` string provided to the :meth:`waves.builders.abaqus_journal` and
:meth:`waves.builders.abaqus_solver` builders is part of the build signature. Changes to these options will trigger a
re-build of that task.

Sometimes you may want to exclude elements of the task action from the build signature. For instance, the Solve step
introduced in :ref:`tutorial_simulation_waves` can run Abaqus with a different number of cpus, which shouldn't affect
the simulation results. Adding a variable number of cpus to the ``abaqus_options`` would change the build signature each
time the cpu count changed and unnecessarily re-run the simulation task. To avoid this, you can specify elements of the
action to exclude from the build signature with the ``$( excluded string $)`` syntax.

**********
References
**********

* `SCons`_ Variable Substitution :cite:`scons-man`

The relevant portion of the `SCons`_ documentation can't be hyperlinked directly. Instead, the relevant portion of the
"Substitution Variables" section of the man pages is quoted below :cite:`scons-man`.

   When a build action is executed, a hash of the command line is saved, together with other information about the
   target(s) built by the action, for future use in rebuild determination. This is called the *build signature* (or *build
   action signature*). The escape sequence **$(** *subexpression* **$)** may be used to indicate parts of a command line that may
   change without causing a rebuild--that is, which are not to be included when calculating the build signature. All text
   from **$(** up to and including the matching **$)** will be removed from the command line before it is added to the build
   signature while only the **$(** and **$)** will be removed before the command is executed. For example, the command line string:

   .. code-block:: bash

      "echo Last build occurred $( $TODAY $). > $TARGET"

   would execute the command:

   .. code-block:: bash

      echo Last build occurred $TODAY. > $TARGET

   but the build signature added to any target files would be computed from:

   .. code-block:: bash

      echo Last build occurred  . > $TARGET

***********
Environment
***********

.. include:: tutorial_environment_activation.txt

*******************
Directory Structure
*******************

3. Create a directory ``tutorial_pseudo_variables`` in the ``waves-eabm-tutorial`` directory.

.. code-block:: bash

   $ pwd
   /path/to/waves-eabm-tutorial
   $ mkdir -p tutorial_pseudo_variables eabm_package_cubit

4. Copy the ``tutorial_04_simulation/SConscript`` file into the newly created ``tutorial_pseudo_variables``
   directory.

.. code-block:: bash

   $ pwd
   /path/to/waves-eabm-tutorial
   $ cp tutorial_04_simulation/SConscript tutorial_pseudo_variables/

.. _tutorial_pseudo_variables_waves_SConscript:

**********
SConscript
**********

A ``diff`` against the ``SConscript`` file from :ref:`tutorial_simulation_waves` is included below to help identify the
changes made in this tutorial.

.. admonition:: waves-eabm-tutorial/tutorial_pseudo_variables/SConscript

   .. literalinclude:: tutorial_pseudo_variables_SConscript
      :language: Python
      :diff: tutorial_04_simulation_SConscript

**********
SConstruct
**********

A ``diff`` against the ``SConstruct`` file from :ref:`tutorial_simulation_waves` is included below to help identify the
changes made in this tutorial.

.. admonition:: waves-eabm-tutorial/SConstruct

   .. literalinclude:: eabm_tutorial_pseudo_variables_SConstruct
      :language: Python
      :diff: eabm_tutorial_04_simulation_SConstruct

*************
Build Targets
*************

6. Build the new targets

.. code-block:: bash

   $ pwd
   /path/to/waves-eabm-tutorial
   $ scons tutorial_pseudo_variables

************
Output Files
************

Explore the contents of the ``build`` directory using the ``tree`` command against the ``build`` directory, as shown
below. Note that the output files from the previous tutorials also exist in the ``build`` directory, but the directory
is specified by name to reduce clutter in the ouptut shown.

.. code-block:: bash

   $ pwd
   /home/roppenheimer/waves-eabm-tutorial
   $ tree build/tutorial_pseudo_variables/
   build/tutorial_pseudo_variables/
