.. _scons_multiactiontask:

########################
SCons Multi-Action Tasks
########################

.. include:: scons_tutorial_introduction.txt

Most build systems use intermediate target files to identify which tasks need to be performed again on subsequent
execution. The :ref:`scons_quickstart` uses this behavior to allow conditional re-building of partial workflows. For
example, if the ``single_element_mesh.py`` journal file changes, the geometry and partitioning tasks do not need to be
re-executed because the ``single_element_geometry.cae`` and ``single_element_paritition.cae`` targets do not depend on
the source ``single_element_mesh.py``.

This conditional re-build granularity comes at the cost of roughly tripling the disk space required to store the Abaqus
CAE files. Sometimes disk space is limited, such as for large models where even a single copy of the file may consume
large amounts of disk space or when a smaller model is built in a large parameteric study. In these cases it is
necessary to operate on a common file from multiple actions. `SCons`_ provides a solution to this by allowing a task
definition to include a list of actions. The state machine stored by `Scons`_ will not store the target state until all
actions have been performed, which avoids re-build state ambiguity when performing more than one action on a single
file.  While this does save storage resources, it will increase computational cost of the re-build because every source
file in the task definition requires the entire task to be re-executed.

***********
Environment
***********

.. include:: scons_tutorial_environment.txt

*******************
Directory Structure
*******************

.. include:: scons_tutorial_directory.txt

***************
SConstruct File
***************

6. Create a file named ``scons_multiactiontask_SConstruct`` from the contents below.

.. admonition:: waves-tutorials/scons_multiactiontask_SConstruct

    .. literalinclude:: tutorials_scons_multiactiontask_SConstruct
       :language: Python
       :lineno-match:

A ``diff`` against the SConstruct file from :ref:`scons_quickstart` is included below to help identify the changes made
in this tutorial. Note that the ``AbaqusJournal`` builder is no longer used. While it would be possible to adapt the
builder to the multi-action journal file execution, in general the files executed by each action may not have a
sufficiently similar command line interface (CLI) or naming convention to generalize a multi-task builder. Instead, the
more flexible, general purpose `SCons Command`_ builder is used.

..  admonition:: waves-tutorials/SConstruct

  .. literalinclude:: tutorials_scons_multiactiontask_SConstruct
     :language: python
     :diff: tutorials_scons_quickstart_SConstruct

****************
Building targets
****************

.. code-block::

   $ pwd
   /home/roppenheimer/waves-tutorials
   $ scons --sconstruct=scons_multiactiontask_SConstruct single_element

.. note::

   The ``--sconstruct`` option is required because the quickstart project configuration file name doesn't follow the
   `SCons`_ naming convention, ``SConstruct``.

************
Output Files
************

There are fewer files than in :ref:`scons_quickstart` because the intermediate targets,
``single_element_geometry.{cae,jnl}`` and ``single_element_partition.{cae,jnl}`` are no longer created. In the case of
the ``*.jnl`` files, this is because Abaqus write the journal file name to match the model name, which is now
``single_element_mesh`` in all journal files.

.. code-block:: bash

   $ pwd
   /home/roppenheimer/waves-tutorials
   $ tree build_scons_multiactiontask/
   build_scons_multiactiontask/
   |-- abaqus.rpy
   |-- abaqus.rpy.1
   |-- abaqus.rpy.2
   |-- assembly.inp
   |-- boundary.inp
   |-- field_output.inp
   |-- history_output.inp
   |-- materials.inp
   |-- parts.inp
   |-- single_element_compression.com
   |-- single_element_compression.dat
   |-- single_element_compression.inp
   |-- single_element_compression.msg
   |-- single_element_compression.odb
   |-- single_element_compression.prt
   |-- single_element_compression.sta
   |-- single_element_mesh.cae
   |-- single_element_mesh.inp
   `-- single_element_mesh.jnl

   0 directories, 19 files
