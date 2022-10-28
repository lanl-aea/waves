.. _tutorial_partition_mesh_waves:

###############################
Tutorial 02: Partition and Mesh
###############################

**********
References
**********

* Adding to `PYTHONPATH`_ with `SCons PrependENVPath`_ method :cite:`scons-user`
* `Abaqus Node Sets`_ :cite:`ABAQUS`
* `Abaqus Element Sets`_ and `Abaqus Elements Guide`_ :cite:`ABAQUS`
* `Abaqus Assembly Definition`_ :cite:`ABAQUS`

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
   $ mkdir tutorial_02_partition_mesh

4. Copy the ``tutorial_01_geometry`` file into the newly created ``tutorial_02_partition_mesh`` directory.

.. code-block:: bash

   $ pwd
   /path/to/waves-eabm-tutorial
   $ cp tutorial_01_geometry tutorial_02_partition_mesh/

.. _tutorials_tutorial_partition_mesh_waves:

**********
SConscript
**********

5. Modify your ``tutorial_02_partition_mesh`` file by adding the contents below immediately after the code
   pertaining to ``# Geometry`` from the previous tutorial.

.. admonition:: waves-eabm-tutorial/tutorial_02_partition_mesh

   .. literalinclude:: tutorials_tutorial_02_partition_mesh
      :language: Python
      :lineno-match:
      :start-after: marker-2
      :end-before: marker-3

Just like building the geometry in :ref:`tutorial_geometry_waves`, the code you just added instructs SCons on how to
build the targets for partitioning and meshing our single element part. Again, the ``journal_file`` variable exists
solely to minimize hard-coded duplication of the strings ``'single_element_partition'`` and ``'single_element_mesh'``.

In the code pertaining to ``# Partition``, we will again pass an empty string for the ``journal_options``. We will
re-open the discussion of using the journal file's command line interface via the ``journal_options`` variable in
:ref:`tutorial_parameter_substitution_waves`. Next, the ``workflow`` list is extended once again to include the action
to use the :meth:`waves.builders.abaqus_journal` builder. The ``target`` list specifies the files created by the
:meth:`waves.builders.abaqus_journal` task's action, and the ``source`` list specifies on which files to act in order to
produce the targets.

Keen readers will note that this source-target definition is slightly different
from that in :ref:`tutorial_geometry_waves`.  Here, we still specify only one target -
``single_element_partition.cae``. This target is geneated by *performing an action on not one, but now two sources*. The
first source is similar to that in :ref:`tutorial_geometry_waves`, where we run the ``single_element_partition.py`` file
in the Abaqus kernel, but now the default behavior of the journal is different.

.. TODO: figure out how to link to a specific entry in the CLI. There's gotta be some way to do this similat to :meth:
   directive. https://re-git.lanl.gov/aea/python-projects/waves/-/issues/175

6. Investigate the :ref:`waves_eabm_cli` documentation for the :ref:`abaqus_single_element_partition_cli` file. Notice that
   a new parameter is defined here that was absent in ``single_element_geometry.py``. This parameter is defined in short
   with ``-i`` or verbosely by ``--input-file``.

The ``--input-file`` command line argument defaults to the string ``'single_element_geometry'`` and does not require a
file extension. So, we simply need to make sure that the ``single_element_geometry.cae`` file (which is an output from
the code we wrote in :ref:`tutorial_geometry_waves`) be included in the ``source`` list. If
``single_element_geometry.cae`` were left out of the source list, the SCons build system would not be able to determine
that the partition target depends on the geometry target. This would result in an indeterminate race condition in target
execution order. Incomplete source and target lists also make it impossible for the build system to automatically
determine when a target needs to be re-built. If not specified as a source, the ``single_element_geometry.cae`` file
could change and the build system would not know that the ``single_element_partition.cae`` target needs to be re-built.

With the two sources defined, the :meth:`waves.builders.abaqus_journal` builder has all the information it needs to
build the ``single_element_partition.cae`` target.

In the code pertaining to ``# Mesh``, the trend continues. We will re-assign the ``journal_file`` variable to the
meshing journal file name  to reduce hard-coded duplication of strings. We define an empty string for
``journal_options``, as nothing other than the default is required for this task. We finally extend the workflow to
utilize the :meth:`waves.builders.abaqus_journal` builder on the ``source`` list. Just like the code for ``#
Partition``, we have two sources. In this tutorial, we rely on the ``single_element_mesh.py`` CLI default arguments
which will use the ``single_element_partition.cae`` file as the input model file. Readers are encouraged to return to
the :ref:`waves_eabm_cli` to become familiar with the command line arguments available for the journal files in this
tutorial.

The ``target`` list, however, shows another difference with the behavior we have seen previously. Now, we have two
targets instead of one. You should now be familiar with the behavior that generates the ``single_element_mesh.cae``
target. The new target is the ``single_element_mesh.inp`` file. This file is called an *orphan mesh* file. When the
:meth:`waves.builders.abaqus_journal` builder acts on the ``single_element_mesh.py`` file, our two target files are
created. The orphan mesh file is created by calling the ``export_mesh()`` function within the ``single_element_mesh.py``
file. See the :ref:`waves_eabm_api` for the :ref:`sphinx_abaqus_journal_utilities_api` file for more information about
the ``export_mesh()`` function.

In summary of the changes you just made to the ``tutorial_02_partition_mesh`` file, a ``diff`` against the
``SConscript`` file from :ref:`tutorial_geometry_waves` is included below to help identify the changes made in this
tutorial.

.. admonition:: waves-eabm-tutorial/tutorial_02_partition_mesh

   .. literalinclude:: tutorials_tutorial_02_partition_mesh
      :language: Python
      :diff: tutorials_tutorial_01_geometry

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
contains a ``main()`` function with `PEP-287`_ formatted docstrings. Within that ``main()`` function is Abaqus python
code that does a few specific tasks:

* Format the ``--input-file`` and ``--output-file`` command line argument values with ``.cae`` file extensions
* Copy the ``input_file`` to an identical ``output_file`` with a new name. This is necessary because Abaqus changes the
  contents of ``*.cae`` files on open. The content change will cause the build system to always re-run the task that
  generated the ``input_file``.
* Within the new ``output_file``, do the following:

  * Create node sets at four corners of the single element part. See the `Abaqus Node Sets`_ documentation :cite:`ABAQUS` for more
    information about node sets.
  * Create node sets for the four sides of the single element part.

* Save the ``output_file`` with the changes made

The :ref:`abaqus_single_element_partition_cli` script also contains an argument parser function, whose auto-generated
CLI documentation can be found in the :ref:`waves_eabm_cli`. The argument parser functions in a very similar way to that
in the ``single_element_geometry.py`` file, but a new command line argument ``--input-file`` is added. This command line
argument is how the script knows which file to copy and then modify in the Abaqus python code.

Lastly, the execution of the ``main()`` function is protected within the context of a ``if __name__ == "__main__":``
statement, and the ``main()`` function is called within ``sys.exit()`` for exit code retrieval.

8. In the ``eabm_package/abaqus`` directory, create a file called ``abaqus_journal_utilities.py`` using the contents
   below.

.. admonition:: waves-eabm-tutoria/eabm_package/abaqus/abaqus_journal_utilities.py

   .. literalinclude:: abaqus_abaqus_journal_utilities.py
      :language: Python
      :lineno-match:
      :end-before: marker-1

The ``abaqus_journal_utilities.py`` script's purpose is to contain commonly used functions that we do not want to
duplicate. At the moment, we have only created one function - ``export_mesh()``. The ``export_mesh`` function utilizes
an `Abaqus Model Object`_ :cite:`ABAQUS` along with a ``part_name`` and ``orphan_mesh_file`` name to create an
orphan mesh file. Orphan mesh files define the entire part's mesh in a text-based file. The node and element locations
and labels are listed in a tabular format that the Abaqus file parser understands.

9. In the ``eabm_package/abaqus`` directory, create a file called ``single_element_mesh.py`` using all the contents
   below.

.. admonition:: waves-eabm-tutorial/eabm_package/abaqus/single_element_mesh.py

    .. literalinclude:: abaqus_single_element_mesh.py
        :language: Python
        :lineno-match:

The ``single_element_mesh.py`` file will have many similarities in code structure to the ``single_element_geometry.py``
and ``single_element_partition.py`` files. The first significant change is within the ``import`` statements at the top
of the file. The ``single_element_mesh.py`` file uses the ``export_mesh()`` function that is imported from the
``abaqus_journal_utilities.py`` file you just created. ``abaqus_journal_utilities.py`` exists in the
``eabm_package/abaqus`` directory, and is never copied to the build directory.

It is possible to use a normal looking import statement because we will modify `PYTHONPATH`_ in the project
``SConstruct`` configuration file. Abaqus Python and Python 3 environments will both inherit the `PYTHONPATH`_ and
search for packages on the paths in this environment variable. While this path modification would be bad practice for a
Python package, since we aren't packaging and deploying our modsim Python modules this path modification is required.
Care should still be taken to avoid naming conflicts between the modsim package directory and any Python packages that
may exist in the active Conda environment.

.. note::

   The ``single_element_mesh.py`` script is also never copied to the build directory, so we can utilize the path of the
   ``single_element_mesh.py`` file to point to the location of the ``abaqus_journal_utilities`` file as well. The journal
   files are executed via absolute path from within the build directory, so the output from these scripts is placed in
   the build directory.

From this point, the ``main()`` function proceeds to copy the input file just like in ``single_element_partition.py``.
The code that follows performs the following tasks within the new ``output_file``:

* Create a part instance that can be meshed. See the `Abaqus Assembly Definition`_ documentation :cite:`ABAQUS` for
  more information about defining parts, part instances, and assemblies.
* Seed the part using the ``--global-seed`` command line argument value to define the global meshing size
* Mesh the part
* Assign an element type to the part. See the `Abaqus Elements Guide`_ :cite:`ABAQUS` for more information about
  defining element types.
* Define element and node sets for elements and nodes that may require output requests in the model. See the `Abaqus
  Element Sets`_ documentation :cite:`ABAQUS` for more information about element sets.
* Create an orphan mesh file by calling the ``export_mesh()`` function that was imported from
  ``abaqus_journal_utilities.py``
* Save the ``output_file`` with the changes made

The ``single_element_mesh.py`` script also contains an argument parser function. This command line interface has yet
another new argument ``--global-seed``. This argument defines global mesh sizing for the model and has a default value
that is assigned to the ``global_seed`` variable if not specified when calling the script.

All other aspects of the ``single_element_mesh.py`` file are the same as ``single_element_partition.py``.

**********
SConstruct
**********

10. Add ``tutorial_02_partition_mesh`` to the ``workflow_configurations`` list in the
    ``waves-eabm-tutorial/SConscruct`` file.

A ``diff`` against the SConstruct file from :ref:`tutorial_geometry_waves` is included below to help identify the
changes made in this tutorial.

   ..  admonition:: waves-eabm-tutorial/SConstruct

     .. literalinclude:: tutorials_tutorial_02_partition_mesh_SConstruct
        :language: python
        :diff: tutorials_tutorial_01_geometry_SConstruct

Note the `PYTHONPATH`_ modification by `SCons PrependENVPath`_. This modification to the project's construction
environment will allow Abaqus Python to import the project module files used by ``single_element_mesh.py``.

*************
Build Targets
*************

5. Build the new targets

.. code-block:: bash

    $ pwd
    /path/to/waves-eabm-tutorial
    $ scons tutorial_02_partition_mesh
    scons: Reading SConscript files ...
    Checking whether abq2021 program exists.../apps/abaqus/Commands/abq2021
    Checking whether abq2020 program exists.../apps/abaqus/Commands/abq2020
    scons: done reading SConscript files.
    scons: Building targets ...
    cd /home/roppenheimer/waves-eabm-tutorial/build/tutorial_02_partition_mesh && /apps/abaqus/Commands/abaqus -information
    environment > single_element_geometry.abaqus_v6.env
    cd /home/roppenheimer/waves-eabm-tutorial/build/tutorial_02_partition_mesh && /apps/abaqus/Commands/abaqus cae -noGui
    /home/roppenheimer/waves-eabm-tutorial/eabm_package/abaqus/single_element_geometry.py -- > single_element_geometry.stdout 2>&1
    cd /home/roppenheimer/waves-eabm-tutorial/build/tutorial_02_partition_mesh && /apps/abaqus/Commands/abaqus -information
    environment > single_element_partition.abaqus_v6.env
    cd /home/roppenheimer/waves-eabm-tutorial/build/tutorial_02_partition_mesh && /apps/abaqus/Commands/abaqus cae -noGui
    /home/roppenheimer/waves-eabm-tutorial/eabm_package/abaqus/single_element_partition.py -- > single_element_partition.stdout 2>&1
    cd /home/roppenheimer/waves-eabm-tutorial/build/tutorial_02_partition_mesh && /apps/abaqus/Commands/abaqus -information
    environment > single_element_mesh.abaqus_v6.env
    cd /home/roppenheimer/waves-eabm-tutorial/build/tutorial_02_partition_mesh && /apps/abaqus/Commands/abaqus cae -noGui
    /home/roppenheimer/waves-eabm-tutorial/eabm_package/abaqus/single_element_mesh.py -- > single_element_mesh.stdout 2>&1
    scons: done building targets.

************
Output Files
************

Explore the contents of the ``build`` directory using the ``tree`` command against the ``build`` directory, as shown
below.

.. code-block:: bash

   $ pwd
   $ /home/roppenheimer/waves-eabm-tutorial
   $ tree build/tutorial_01_geometry/ build/tutorial_02_partition_mesh/
   build/tutorial_01_geometry/
   |-- abaqus.rpy
   |-- single_element_geometry.abaqus_v6.env
   |-- single_element_geometry.cae
   |-- single_element_geometry.jnl
   `-- single_element_geometry.stdout
   build/tutorial_02_partition_mesh/
   |-- abaqus.rpy
   |-- abaqus.rpy.1
   |-- abaqus.rpy.2
   |-- single_element_geometry.abaqus_v6.env
   |-- single_element_geometry.cae
   |-- single_element_geometry.jnl
   |-- single_element_geometry.stdout
   |-- single_element_mesh.abaqus_v6.env
   |-- single_element_mesh.cae
   |-- single_element_mesh.inp
   |-- single_element_mesh.jnl
   |-- single_element_mesh.stdout
   |-- single_element_partition.abaqus_v6.env
   |-- single_element_partition.cae
   |-- single_element_partition.jnl
   `-- single_element_partition.stdout

   0 directories, 21 files

Examine the contents of the ``build/tutorial_01_geometry`` and a ``build/tutorial_02_partition_mesh`` directories.
Recall from the note this tutorials_tutorial's :ref:`tutorial_partition_mesh_waves` section that we require the targets
from the code pertaining to :ref:`tutorial_geometry_waves` to build the targets for this tutorial. There is an important
distinction to be made here. This tutorial is **NOT** utilizing the outputs from :ref:`tutorial_geometry_waves`'s
:ref:`tutorial_geometry_waves_build_targets` section when we executed the ``$ scons tutorial_01_geometry`` command. This
tutorial is utilizing the outputs generated from executing the same code, but from our new
``tutorial_02_partition_mesh`` file. For this reason, we see the same outputs from the
``build/tutorial_01_geometry`` directory in the ``build/tutorial_02_partition_mesh`` directory (along with other
:ref:`tutorial_partition_mesh_waves` output files).

The new output files pertain to the partitioning and meshing steps we added to the workflow. The file extensions are the
same as when we ran the geometry workflow, but now we have an added ``single_element_mesh.inp`` orphan mesh file.
