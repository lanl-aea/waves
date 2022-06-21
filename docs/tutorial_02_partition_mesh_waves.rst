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

7. In the ``eabm_package/abaqus`` directory, create a file called ``single_element_partition.py`` using all the contents 
   below.

.. admonition:: waves-eabm-tutorial/eabm_package/abaqus/single_element_partition.py
   
    .. literalinclude:: abaqus_single_element_partition.py
        :language: Python
        :lineno-match:

The ``single_element_partition.py`` file is layed out in a very similar fashion to ``single_element_geometry.py``. It 
contains a ``main()`` function with `PEP-287` formatted docstrings. Within that main function is Abaqus python code that 
does a few specific tasks:

* Format the ``--input-file`` and ``--output-file`` command line arguments with file extensions
* Copy the ``input_file`` to an identical ``output_file`` with a new name
* Within the new ``output_file``, do the following:

  * Create node sets at four corners of the single element part. See the `Abaqus Node Sets`_ documentation for more 
    information about node sets.
  * Create surfaces for the four sides of the single element part. See the `Abaqus Surfaces`_ documentation for more 
    information about surfaces.

* Save the ``output_file`` with the changes made

The ``single_element_partition.py`` script also contains an argument parser function, whose auto-generated CLI 
documentation can be found in the :ref:`sphinx_cli`. The argument parser functions in a very similar way to that in the 
``single_element_geometry.py`` file, but a new command line argument ``--input-file`` is added. This command line 
argument is how the script knows which file to copy and then modify in the Abaqus python code.

Lastly, the execution of the ``main()`` function is protected within the context of a ``if __name__ == "__main__":`` 
statement, and the ``main()`` function is called within ``sys.exit()`` for exit code retrieval.

8. in the ``eabm_package/abaqus`` directory, create a file called ``abaqus_journal_utilities.py`` using the contents 
   below.

.. admonition:: waves-eabm-tutoria/eabm_package/abaqus/abaqus_journal_utilities.py
   
   .. literalinclude:: abaqus_abaqus_journal_utilities.py
      :language: Python
      :lineno-match:
      :end-before: marker-1

The ``abaqus_journal_utilities.py`` script's purpose is to contain commonly used functions that we do not want to 
duplicate. At the moment, we have only created one function - ``export_mesh()``. The ``export_mesh`` function utlizes an 
`Abaqus Model Object`_ along with a ``part_name`` and ``orphan_mesh_file`` name to create an orphan mesh file. Orphan 
mesh files define the an entire part's mesh in a text-based file. The node and element locations and labels are listed 
in a tabular format that the Abaqus file parser understands.

.. note::
   
   Any model developer may have other functions that are commonly used by multiple scripts. An example use case is if 
   our model has multiple parts that notionally all looked the same. In this case, the model developer could choose to 
   create a generic geometry generation function and place it in this ``abaqus_journal_utilities.py`` file. The model 
   developer can then call this function any number of times without duplicating source code.

9. In the ``eabm_package/abaqus`` directory, create a file called ``single_element_mesh.py`` using all the contents 
   below.

.. admonition:: waves-eabm-tutorial/eabm_package/abaqus/single_element_mesh.py
   
    .. literalinclude:: abaqus_single_element_mesh.py
        :language: Python
        :lineno-match:

The ``single_element_mesh.py`` file will have many similarities in code structure to the ``single_element_geometry.py`` 
and ``single_element_partition.py`` files. The first significant change is in the ``import`` statements at the top of 
the file. The ``single_element_mesh.py`` file uses a function called ``export_mesh`` that is imported from the 
``abaqus_journal_utilities.py`` file you just created. ``abaqus_journal_utlities.py`` exists in the 
``eabm_package/abaqus`` directory, and is never copied to the builder directory where the journal files are ran with the 
Abaqus kernel. Without any modifications to your ``PYTHONOATH``, the Abaqus kernel will attempt to import 
``abaqus_journal_utilities``, but will not be able to find that file (because it is not in the build directory). In 
order to solve this problem, we must add the location of the ``abaqus_journal_utlities.py`` file to ``$PYTHONPATH`` at 
run time.

.. note::
   
   While the ``single_element_mesh.py`` script is also never copied to the run directory, it is executed via absolute 
   path from within the run directory. For this reason, we can utilize the path of the ``single_element_mesh.py`` file 
   to point to the location of the ``abaqus_journal_utlities`` file as well.

First, the ``filename`` is extracted in the same as in :ref:`tutorial_geometry_waves` in the 
:ref:`tutorial_geometry_waves_command_line_interfaces` code. Then, we use ``sys.path.insert`` from the `Python sys`_ 
package to add the location of the current file (``single_element_mesh.py``) to the ``PYTHONPATH``.

From this point, the ``main()`` function proceeds to copy the input file just like in ``single_element_partition.py``. 
The code that follows performs the following tasks within the new ``output_file``:

* Create a part instance that can be meshed
* Seed the part using the ``global_seed`` command line argument value to define the global meshing size
* Mesh the part
* Assign an element type to the part
* Define element and node sets for all elements and all nodes in the model. See the `Abaqus Element Sets`_ documentation 
  for more information about element sets
* Create an orphan mesh file by calling the ``export_mesh()`` function that was imported from 
  ``abaqus_journal_utilities.py``
* Save the ``output_file`` with the changes made

The ``single_element_mesh.py`` script also contains an argument parser function. This command line interfaces has yet 
another new argument ``--global-seed``. This argument defines global mesh sizing for the model and has a default value 
that is assigned to the ``global_seed`` variable if not specified when calling the script.

All other aspects of the ``single_element_mesh.py`` file are the same as ``single_element_partition.py``.

**********
SConstruct
**********

10. Add ``tutorial_02_partition_mesh`` to the ``eabm_simulation_directories`` list in the 
    ``waves-eabm-tutorial/SConscruct`` file.

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
    scons: Reading SConscript files ...
      warnings.warn(
    Checking whether sphinx-build program exists.../projects/aea_compute/aea-beta/bin/sphinx-build
    Checking whether abaqus program exists.../apps/abaqus/Commands/abaqus
    Checking whether cubit program exists.../apps/Cubit-15.8/cubit
    scons: done reading SConscript files.
    scons: Building targets ...
    cd /home/roppenheimer/waves-eabm-turorial/build/tutorial_02_partition_mesh && /apps/abaqus/Commands/abaqus -information 
    environment > single_element_geometry.abaqus_v6.env
    cd /home/roppenheimer/waves-eabm-turorial/build/tutorial_02_partition_mesh && /apps/abaqus/Commands/abaqus cae -noGui 
    /home/roppenheimer/waves-eabm-turorial/eabm_package/abaqus/single_element_geometry.py -- > single_element_geometry.stdout 2>&1
    cd /home/roppenheimer/waves-eabm-turorial/build/tutorial_02_partition_mesh && /apps/abaqus/Commands/abaqus -information 
    environment > single_element_partition.abaqus_v6.env
    cd /home/roppenheimer/waves-eabm-turorial/build/tutorial_02_partition_mesh && /apps/abaqus/Commands/abaqus cae -noGui 
    /home/roppenheimer/waves-eabm-turorial/eabm_package/abaqus/single_element_partition.py -- > single_element_partition.stdout 2>&1
    cd /home/roppenheimer/waves-eabm-turorial/build/tutorial_02_partition_mesh && /apps/abaqus/Commands/abaqus -information 
    environment > single_element_mesh.abaqus_v6.env
    cd /home/roppenheimer/waves-eabm-turorial/build/tutorial_02_partition_mesh && /apps/abaqus/Commands/abaqus cae -noGui 
    /home/roppenheimer/waves-eabm-turorial/eabm_package/abaqus/single_element_mesh.py -- > single_element_mesh.stdout 2>&1
    scons: done building targets.

************
Output Files
************

Explore the contents of the ``build`` directory using the ``tree`` command against the ``build`` directory, as shown 
below. 

.. code-block:: bash
   
    $ pwd
    $ /home/roppenheimer/waves-eabm-tutorial
    $ tree build/
    build/
    ├── docs
    │   └── SConscript
    ├── tutorial_01_geometry
    │   ├── abaqus.rpy
    │   ├── single_element_geometry.abaqus_v6.env
    │   ├── single_element_geometry.cae
    │   ├── single_element_geometry.jnl
    │   └── single_element_geometry.stdout
    └── tutorial_02_partition_mesh
        ├── abaqus.rpy
        ├── abaqus.rpy.1
        ├── abaqus.rpy.2
        ├── single_element_geometry.abaqus_v6.env
        ├── single_element_geometry.cae
        ├── single_element_geometry.jnl
        ├── single_element_geometry.stdout
        ├── single_element_mesh.abaqus_v6.env
        ├── single_element_mesh.cae
        ├── single_element_mesh.inp
        ├── single_element_mesh.jnl
        ├── single_element_mesh.stdout
        ├── single_element_partition.abaqus_v6.env
        ├── single_element_partition.cae
        ├── single_element_partition.jnl
        └── single_element_partition.stdout

    3 directories, 22 files

