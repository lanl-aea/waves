.. _scons_multiactiontask:

########################
SCons Multi-Action Tasks
########################

.. include:: scons_tutorial_introduction.txt

Most build systems use intermediate target files to identify which tasks need to be performed again on subsequent
execution. The :ref:`scons_quickstart` uses this behavior to allow conditional re-building of partial workflows. For
example, if the ``rectangle_mesh.py`` journal file changes, the geometry and partitioning tasks do not need to be
re-executed because the ``rectangle_geometry.cae`` and ``rectangle_paritition.cae`` targets do not depend on
the source ``rectangle_mesh.py``.

This conditional re-build granularity comes at the cost of roughly tripling the disk space required to store the Abaqus
CAE files. Sometimes disk space is limited, such as for large models where even a single copy of the file may consume
large amounts of disk space or when a smaller model is built in a large parameteric study. In these cases it is
necessary to operate on a common file from multiple actions. `SCons`_ provides a solution to this by allowing a task
definition to include a list of actions. The state machine stored by `Scons`_ will not store the target state until all
actions have been performed, which avoids re-build state ambiguity when performing more than one action on a single
file. While this does save storage resources, it will increase computational cost of the re-build because every source
file in the task definition requires the entire task to be re-executed.

**********
References
**********

* `SCons Command`_ :cite:`scons-user`

***********
Environment
***********

.. include:: scons_tutorial_environment.txt

*******************
Directory Structure
*******************

3. Create the project directory structure and copy the Multi-Action Task source files into the
   ``~/waves-tutorials/multi_action_task`` sub-directory with the :ref:`waves_cli` :ref:`waves_fetch_cli` subcommand.

.. code-block:: bash

      $ waves fetch tutorials/multi_action_task --destination ~/waves-tutorials/multi_action_task
      WAVES fetch
      Destination directory: '/home/roppenheimer/waves-tutorials/multi_action_task'
      $ cd ~/waves-tutorials/multi_action_task
      $ pwd
      /home/roppenheimer/waves-tutorials/multi_action_task

***************
SConscript File
***************

The SConscript file below contains the workflow task definitions, where a task is a list of sources, an action to
operate on those sources, and the targets that the action produces. The :ref:`build_system` discussion includes a more
detailed review of build systems.

.. admonition:: multi_action_task/SConscript

    .. literalinclude:: multi_action_task_SConscript
       :language: Python
       :lineno-match:

A ``diff`` against the SConstruct file from :ref:`scons_quickstart` is included below to help identify the changes made
in this tutorial. Note that the ``AbaqusJournal`` builder is no longer used. While it would be possible to adapt the
builder to the multi-action journal file execution, in general the files executed by each action may not have a
sufficiently similar command-line interface (CLI) or naming convention to generalize a multi-task builder. Instead, the
more flexible, general purpose `SCons Command`_ builder is used.

..  admonition:: waves-tutorials/SConstruct

  .. literalinclude:: multi_action_task_SConscript
     :language: python
     :diff: scons_quickstart_SConscript

****************
Building targets
****************

.. code-block::

   $ pwd
   /home/roppenheimer/waves-tutorials/multi_action_task
   $ scons rectangle

************
Output Files
************

There are fewer files than in :ref:`scons_quickstart` because the intermediate targets,
``rectangle_geometry.{cae,jnl}`` and ``rectangle_partition.{cae,jnl}`` are no longer created. In the case of
the ``*.jnl`` files, this is because Abaqus write the journal file name to match the model name, which is now
``rectangle_mesh`` in all journal files.

.. code-block:: bash

   $ pwd
   /home/roppenheimer/waves-tutorials/multi_action_task
   $ tree build/
   build/
   ├── abaqus_utilities.py
   ├── abaqus.rpy
   ├── abaqus.rpy.1
   ├── abaqus.rpy.2
   ├── assembly.inp
   ├── boundary.inp
   ├── field_output.inp
   ├── history_output.inp
   ├── materials.inp
   ├── parts.inp
   ├── rectangle_compression.com
   ├── rectangle_compression.dat
   ├── rectangle_compression.inp
   ├── rectangle_compression.msg
   ├── rectangle_compression.odb
   ├── rectangle_compression.prt
   ├── rectangle_compression.sta
   ├── rectangle_geometry.py
   ├── rectangle_mesh.cae
   ├── rectangle_mesh.inp
   ├── rectangle_mesh.jnl
   ├── rectangle_mesh.py
   ├── rectangle_partition.py
   └── SConscript

   0 directories, 24 files

**********************
Workflow Visualization
**********************

.. code-block::

   $ pwd
   /home/roppenheimer/waves-tutorials/multi_action_task
   $ waves visualize rectangle --output-file multi_action_task.png --width=28 --height=6

.. raw:: latex

    \begin{landscape}
        \vspace*{\fill}

.. figure:: multi_action_task.png
   :align: center
   :width: 100%

.. raw:: latex

        \vspace*{\fill}
    \end{landscape}
