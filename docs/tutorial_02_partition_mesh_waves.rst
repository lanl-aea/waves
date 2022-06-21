.. _tutorial_partition_mesh_waves:

###############################
Tutorial 02: Partition and Mesh
###############################

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

3. Create a directory ``tutorial_02_partition_mesh`` in the ``waves-eabm-turorial`` directory.

.. code-block:: bash
   
   $ pwd
   /path/to/waves-eabm-tutorial
   $ mkdir tutorial_05_parameter_substitution

4. Copy the ``tutorial_01_geometry/SConscript`` file into the newly created ``tutorial_02_partition_mesh`` directory.

.. code-block:: bash
   
   $ pwd
   /path/to/waves-eabm-tutorial
   $ cp tutorial_01_geometry/SConscript tutorial_02_partition_mesh/

**********
SConscript
**********

5. Modify your ``tutorial_02_partition_mesh/SConscript`` file by adding the contents below immediately after the code 
   pertaining to ``# Geometry`` from the previous tutorial.

.. admonition:: waves-eabm-tutorial/tutorial_02_partition_mesh/SConscript
   
   .. literalinclude:: tutorial_02_partition_mesh_SConscript
      :language: Python
      :lineno-match:
      :start-after: marker-1
      :end-before: marker-2

Just like building the geometry in :ref:`tutorial_geometry_waves`, the code you just added instructs SCons on how to 
build the targets for partitioning and meshing our single element part. Again, the ``journal_file`` variable exists 
solely to minimize hard-coded duplication of the strings ``'single_element_partition'`` and ``'single_element_mesh'``.

In the code pertaining to ``# Partition``, we will again pass an empty string for the ``journal_options``. We will 
re-open the discussion of using the journal file's command line interface via the ``journal_options`` variable in 
:ref:`tutorial_parameter_substitution_waves`. Next, the ``workflow`` list is extended once again to include the action 
to use the :meth:`waves.builders.abaqus_journal` builder. The ``target`` list specifies the files created by the 
:meth:`waves.builders.abaqus_journal` task's action, and the ``source`` list specifies which files need to be acted on 
in order to produce the targets.

Keen readers will note that this source-target definition is slightly different 
from that in ref:`tutorial_geometry_waves`.  Here, we still specify only one target - 
``single_element_partition.cae``. This target is geneating by performing an action on not one, but now two sources. The 
first source is similar to that in :ref:`tutorial_geometry_waves`, where we run the ``single_element_partition.py`` file 
in the Abaqus kernel, but now the default behavior of the journal is different. 

6. Investigate the :ref:`sphinx_cli` documentation for the ``single_element_partition.py`` file. Notice that a new 
   parameter is defined here that was absent in ``single_element_geometry.py``. This parameter is defined in short with 
   ``-i`` or verbosely by ``--input-file``.

This command line argument defaults to the string ``'single_element)geometry'`` and does not require a file extension. 
So, we simply need to make sure that the ``single_element_geometry.cae`` file (which was an output from 
:ref:`tutorial_geometry_waves`) be included in the ``source`` list. If ``single_element_geometry.cae`` were left out 
of the source list, it is quite possible that the build system would still be able to build our target. However, 
this would lead to possibly unreproducable behavior in the case where something has changed in the 
``single_element_geometry.cae`` file. If not specified as a source, the ``single_element_geometry.cae`` file could 
change and the build system would not know that the ``single_element_partition.cae`` target needs to be updated.

With the two sources defined, the :meth:`waves.builders.abaqus_journal` builder has all the information it needs to 
build the ``single_element_partition.cae`` target.

.. note::
   
   At this point, we have encountered our first dependency on a previous tutorial. It is important to understand that 
   the code pertaining to ``# Partition`` *requires* that the ``single_element_partition.cae`` file be in the build 
   directory at the time the build system gets to the task of acting on our ``# Partition`` sources.
   
   It is the build system's job to define the dependencies for each target. However, the build system cannot utilize a 
   source file that has never been created. The outputs from :ref:`tutorial_geometry_waves` are required sources for
   this tutorial, and this tutorial's outputs will be required sources for the tutorials that follow.

   You cannot build :ref:`tutorial_partition_mesh_waves` without first building :ref:`tutorial_geometry_waves`.

In the code pertaining to ``# Mesh``, the trend continues. We will create a ``journal_file`` variable to reduce 
hard-coded duplication of strings. We define an empty string for ``journal_options``, as nothing other than the default 
is required for this task. We finally extend the workflow to utilize the :meth:`waves.builders.abaqus_journal` builder 
on the ``source list``. Just like the code for ``# Partition``, we have two sources. The ``single_element_mesh.py`` CLI 
defines an ``--input-file`` argument that defaults to ``single_element_partiton.cae``. Readers are encouraged to return 
to the :ref:`sphinx_cli` to become familiar with the command line arguments available for the journal files in this 
tutorial.

The ``target`` list, however, shows another difference with the behavior we have seen previously. Now, we have two 
targets instead of one. You should now be familiar with the behavior that generates the ``single_element_mesh.cae`` 
target. The new target is the ``single_element_mesh.inp`` file. This file is called an *orphan mesh* file. When the 
:meth:`waves.builders.abaqus_journal` builder acts on the ``single_element_mesh.py`` file, our two target files are 
created. The orphan mesh file is created by calling the ``export_mesh()`` function within the ``single_element_mesh.py`` 
file. See the :ref:`sphinx_api`, specifically the :ref:`sphinx_abaqus_journal_utilities_api` API, for more information 
about the ``export_mesh()`` function.


In summary of the changes you just made to the ``tutorial_02_partition_mesh/SConscript`` file, a ``diff`` against the 
``SConscript`` file from :ref:`tutorial_geometry_waves` is included below to help identify the changes made in this 
tutorial.

.. admonition:: waves-eabm-tutorial/tutorial_02_partition_mesh/SConscript
   
   .. literalinclude:: tutorial_02_partition_mesh_SConscript
      :language: Python
      :diff: tutorial_01_geometry_SConscript

*******************
Abaqus Journal File
*******************

Recall from :ref:`tutorial_geometry_waves` that you created an Abaqus journal file called 
``single_element_geometry.py``. You will now create two more for the partitioning and meshing workflows. The reader is 
referred to the following sections in :ref:`tutorial_geometry_waves` for a reminder of different aspects of these 
journal files:

* :ref:`tutorial_geometry_waves_main_functions`
* :ref:`tutorial_geometry_waves_python_docstrings`
* :ref:`tutorial_geometry_waves_abaqus_python_code`
* :ref:`tutorial_geometry_waves_command_line_interfaces`
* :ref:`tutorial_geometry_waves_top_level_code_environment`
* :ref:`tutorial_geometry_waves_retrieving_exit_codes`

.. admonition:: single_element_partition.py
   
    .. literalinclude:: abaqus_single_element_partition.py
        :language: Python
        :lineno-match:

.. admonition:: single_element_mesh.py
   
    .. literalinclude:: abaqus_single_element_mesh.py
        :language: Python
        :lineno-match:

**********
SConstruct
**********

A ``diff`` against the SConstruct file from :ref:`tutorial_geometry_waves` is included below to help identify the 
changes made in this tutorial.

   ..  admonition:: waves-eabm-tutorial/SConstruct

     .. literalinclude:: eabm_tutorial_02_partition_mesh_SConstruct
        :language: python
        :diff: eabm_tutorial_01_geometry_SConstruct

*************
Build Targets
*************

5. Build the new targets

.. code-block:: bash
   
   $ pwd
   /path/to/waves-eabm-tutorial
   $ scons tutorial_02_partition_mesh

************
Output Files
************
