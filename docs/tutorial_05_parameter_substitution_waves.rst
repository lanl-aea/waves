.. _tutorial_parameter_substitution_waves:

###################################
Tutorial 05: Parameter Substitution
###################################

**********
References
**********

* `SCons Substfile`_
* `Abaqus *PARAMETER`_ keyword documentation

***********
Environment
***********

.. include:: tutorial_environment_activation.txt

*******************
Directory Structure
*******************

3. Create a directory ``tutorial_05_parameter_substitution`` in the ``waves-eabm-tutorial`` directory.

.. code-block:: bash

   $ pwd
   /path/to/waves-eabm-tutorial
   $ mkdir tutorial_05_parameter_substitution

4. Copy the ``tutorial_04_simulation/SConscript`` file into the newly created ``tutorial_05_parameter_substitution``
   directory.

.. code-block:: bash

   $ pwd
   /path/to/waves-eabm-tutorial
   $ cp tutorial_04_simulation/SConscript tutorial_05_parameter_substitution/

******************
Solver Input Files
******************

5. Copy the ``eabm_package/abaqus/single_element_compression.inp`` file and all of its contents to a new file in the
   same directory named ``single_element_compression.inp.in``. **Note:** the only change in the file name is the
   addition of the ``.in`` suffix.

.. code-block:: bash

   $ pwd
   /path/to/waves-eabm-tutorial
   $ cp eabm_package/abaqus/single_element_compression.inp eabm_package/abaqus/single_element_compression.inp.in

In this tutorial, we will be modifying several files from :ref:`tutorial_simulation_waves`, the first of which is
``single_element_compression.inp``. We copy this file and all of its contents to a new file with the same basename and
the ``.in`` extension for the purposes of *parameter substitution*. This change is made so it is easy for the
:meth:`waves.builders.copy_substitute` builder to identify which files should be searched for parameters. Any files with
the ``.in`` extension that are passed to the :meth:`waves.builders.copy_substitute` builder will be parsed for
characters matching the parameter definitions using substitution with `SCons Substfile`_. This is discussed in
more detail later in this tutorial.

6. Use the ``diff`` below to modify your ``single_element_compression.inp.in`` file.

.. admonition:: waves-eabm-tutorial/eabm_package/abaqus/single_element_compression.inp.in

   .. literalinclude:: abaqus_single_element_compression.inp.in
      :language: text
      :diff: abaqus_single_element_compression.inp

First, we add the ``displacement`` Abaqus parameter in Python 2 syntax to the ``single_element_compression.inp.in`` file
using the `Abaqus *PARAMETER`_ keyword. Second, we use the parameter value with the Abaqus parameter syntax,
``<displacement>``. Casting the value substituted by the parameter to a ``float`` ensures that the ``displacement``
parameter ends up the proper variable type. Note that the `SCons Substfile`_ builder performs a literal string
substitution in the target file, so it is necessary to prepare the correct syntax for the file type where the
substitution occurs. When type ambiguity may arise, explicit type casting may help in debugging bugs caused by variable
type conversions. For instance, when a float, ``2.0``, is required but a direct string replacement may result in an
integer as ``2``. It's also possible to use the native string replacement, for instance one could use ``str`` as a
parameter to change the name of the material assigned to a part in the model.

The final modification to make to the ``single_element_compression.inp.in`` file is to replace the hardcoded
displacement value of ``-1.0`` with the parameter key ``<displacement>``. With this change, the Abaqus file parser will
know to use the value of the ``displacement`` parameter anywhere it sees ``<displacement>``.

**********
SConscript
**********

7. Modify your ``tutorial_05_parameter_substitution/SConscript`` file by adding the contents shown below to the code
   pertaining to ``# Simulation variables``. The entire code snippet shows how your code should look after editing, and
   the highlghted portion is what needs to be added to your existing code.

.. admonition:: waves-eabm-tutorial/tutorial_05_parameter_substitution/SConscript

   .. literalinclude:: tutorial_05_parameter_substitution_SConscript
      :language: Python
      :lineno-match:
      :start-after: marker-1
      :end-before: marker-2
      :emphasize-lines: 3-9

In the code you just added, a ``simulation_variables`` dictionary is defined. Each key-value pair in the
``simulation_variables`` dictionary defines a parameter that already exists in several of the scripts we have utilized
in the previous tutorials. ``width`` and ``height`` are used in the ``single_element_geometry.py`` and
``single_element_partition.py`` scripts, and ``global_seed`` is used in the ``single_element_mesh.py`` script. Recall
that each of these scripts is called using a command line interface that has default parameters. See the
:ref:`sphinx_cli` to see what the default values are. As mentioned in :ref:`tutorial_geometry_waves`, the argument
parser for each of these scripts will supply a default value for each command line argument that is not specified
(assuming a defualt value was specified in the argument parser definition). This allowed us to simplify the command
passed to the :meth:`waves.builders.abaqus_journal` builder. The advantage to coding this behavior ahead of time is that
we get parameter substitution into our journal files for free. The ``width``, ``height``, and ``global_seed`` keys of
the ``simulation_variables`` dictionary will be used later in this tutorial to specify the values passed to the journal
files via the CLI.

The final key-value pair defined in the ``simulation_variables`` dictionary is ``displacement``. This parameter will be
used in a slightly different way than the others, as the script that utilizes this parameter does not function with a
command line interface. Recall from earlier in this tutorial, we created a new file called
``single_element_compression.inp.in`` and added an `Abaqus *PARAMETER`_ definition with the ``@displacement@`` key.
Here, our final key-value pair of the ``simulation_variables`` dictionary will be utilized after the key transformation
to the ``project_substitution_dictionary`` which adds the ``@`` characters to the ``simulation_variables`` keys.
Disussion of exacly how this is implemented with the :meth:`waves.builders.copy_substitute` builder will come later in
this tutorial.

Finally, we must discuss the last line of your new code, which defines the ``simulation_substitution_dictionary``.
Simply put, the keys of the ``simulation_variables`` dictionary must be uniquely identifiable as parameters in the midst
of all the other text in a file. Note that this step is only required when utilizing the
:meth:`waves.builders.copy_substitute` builder for parameter substitution. In the code you will add next, we will
continue to use the ``simulation_variables`` dictionary, as we do not need uniquely identifiable parameter keys when
values are passed to our scripts via command line interface.

8. Modify your ``tutorial_05_parameter_substitution/SConscript`` file by using the highlighed lines below to modify the
   ``journal_options`` for the code pertaining to ``# Geometry``, ``# Partition``, and ``# Mesh``.

.. admonition:: waves-eabm-tutorial/tutorial_05_parameter_substitution/SConscript

   .. literalinclude:: tutorial_05_parameter_substitution_SConscript
      :language: Python
      :lineno-match:
      :start-after: marker-3
      :end-before: marker-4
      :emphasize-lines: 3, 11, 19

As was previously discussed, we use the key-value pairs of the ``simulation_variables`` dictionary in the arguments we
pass to the command line interfaces for ``single_element_{geometry,partition,mesh}.py``. Using a formatted string as
shown in the first highlighted section, we will end up passing a string that looks like the following to the
``single_element_geometry.py`` CLI:

.. code-block:: python

   journal_options = "--width 1.0 --height 1.0"

This behavior is repeated for the code pertaining to ``# Partition`` and ``# Mesh``.

9. Modify your ``tutorial_05_parameter_substitution/SConscript`` file by using the highlighed lines below to modify the
   code pertaining to ``# SolverPrep``.

.. admonition:: waves-eabm-tutorial/tutorial_05_parameter_substitution/SConscript

   .. literalinclude:: tutorial_05_parameter_substitution_SConscript
      :language: Python
      :lineno-match:
      :start-after: marker-4
      :end-before: marker-5
      :emphasize-lines: 3, 13-14

Per the changes you made earlier in this tutorial, the ``abaqus_source_list`` must be updated to reflect the replacement
of ``single_element_compression.inp`` with the parameterized ``single_element_compression.inp.in`` file.

The final change to be made in the ``tutorial_05_parameter_substitution/SConscript`` file is to utilize the
``substitution_dictionary`` parameter in the usage of the :meth:`waves.builders.copy_substitute` builder.

In this tutorial, we leverage two different builder behaviors when defining sources and targets for the
:meth:`waves.builders.copy_substitute` builder. We are already familiar with one behavior, where the builder simply
copies the source file to the build directory.

This builder uses template substitution with files named with the ``*.in`` extension, and looks to match and replace
*any characters* that match the keys in the provided ``substitution_dictionary``. For this reason, we must make our
parameter names uniquely identifiable (e.g. ``@variable@``).

The second behavior is utilized when we specify a file with ``.in`` extension in the ``abaqus_source_list`` and we
specify a ``substitution_dictionary`` in the builder's options. This behavior will act on any file in the source list
with ``.in`` extension and attempts to match the parameter keys in the ``substitution_dictionary`` with the text in the
file. For this reason, we must make our parameter names identifiable with a templating character (e.g. ``@variable@``).
In this process, the files with ``.in`` extension are not modified, but are first copied to a file of the same name in
the build directory. The contents of the newly copied file are modified to reflect the parameter substitution and the
``.in`` extension is removed as a default behavior of the `SCons Substfile`_ method. The two step copy/substitute
behavior is required to allow SCons to unambiguously resolve the source-target file locations. We will see this behavior
more clearly when we investigate the :ref:`tutorial_parameter_substitution_waves_output_files` for this tutorial.

In summary of the changes you just made to the ``tutorial_05_parameter_substitution`` file, a ``diff`` against the
``SConscript`` file from :ref:`tutorial_simulation_waves` is included below to help identify the
changes made in this tutorial.

.. admonition:: waves-eabm-tutorial/tutorial_05_parameter_substitution/SConscript

   .. literalinclude:: tutorial_05_parameter_substitution_SConscript
      :language: Python
      :diff: tutorial_04_simulation_SConscript

**********
SConstruct
**********

10. Add ``tutorial_05_parameter_substitution`` to the ``eabm_simulation_directories`` list in the
    ``waves-eabm-tutorial/SConstruct`` file.

A ``diff`` against the ``SConstruct`` file from :ref:`tutorial_simulation_waves` is included below to help identify the
changes made in this tutorial.

.. admonition:: waves-eabm-tutorial/SConstruct

   .. literalinclude:: eabm_tutorial_05_parameter_substitution_SConstruct
      :language: Python
      :diff: eabm_tutorial_04_simulation_SConstruct

A previous tutorial constructed the ``simulation_variables`` and the ``substitution_dictionary`` variables. The
``simulation_variables`` dictionary is used to define simulation parameters for SCons project definition and script
command line interfaces. The ``substitution_dictionary`` is constructed from the ``simulation_variables`` dictionary to
apply the parameter substitution syntax (leading and trailing ``@`` character) to each variable name for use with the
``copy_substitute`` method as introduced in the current tutorial.

*************
Build Targets
*************

11. Build the new targets

.. code-block:: bash

    $ pwd
    /path/to/waves-eabm-tutorial
    $ scons tutorial_05_parameter_substitution
    scons: Reading SConscript files ...
      warnings.warn(
    Checking whether sphinx-build program exists.../projects/aea_compute/aea-beta/bin/sphinx-build
    Checking whether abaqus program exists.../apps/abaqus/Commands/abaqus
    Checking whether cubit program exists.../apps/Cubit-15.8/cubit
    scons: done reading SConscript files.
    scons: Building targets ...
    cd /home/roppenheimer/waves-eabm-tutorial/build/tutorial_05_parameter_substitution && /apps/abaqus/Commands/abaqus -information
    environment > single_element_geometry.abaqus_v6.env
    cd /home/roppenheimer/waves-eabm-tutorial/build/tutorial_05_parameter_substitution && /apps/abaqus/Commands/abaqus cae -noGui
    /home/roppenheimer/waves-eabm-tutorial/eabm_package/abaqus/single_element_geometry.py -- --width 1.0 --height 1.0 >
    single_element_geometry.stdout 2>&1
    cd /home/roppenheimer/waves-eabm-tutorial/build/tutorial_05_parameter_substitution && /apps/abaqus/Commands/abaqus -information
    environment > single_element_partition.abaqus_v6.env
    cd /home/roppenheimer/waves-eabm-tutorial/build/tutorial_05_parameter_substitution && /apps/abaqus/Commands/abaqus cae -noGui
    /home/roppenheimer/waves-eabm-tutorial/eabm_package/abaqus/single_element_partition.py -- --width 1.0 --height 1.0 >
    single_element_partition.stdout 2>&1
    cd /home/roppenheimer/waves-eabm-tutorial/build/tutorial_05_parameter_substitution && /apps/abaqus/Commands/abaqus -information
    environment > single_element_mesh.abaqus_v6.env
    cd /home/roppenheimer/waves-eabm-tutorial/build/tutorial_05_parameter_substitution && /apps/abaqus/Commands/abaqus cae -noGui
    /home/roppenheimer/waves-eabm-tutorial/eabm_package/abaqus/single_element_mesh.py -- --global-seed 1.0 >
    single_element_mesh.stdout 2>&1
    Copy("build/tutorial_05_parameter_substitution/single_element_compression.inp.in",
    "eabm_package/abaqus/single_element_compression.inp.in")
    Creating 'build/tutorial_05_parameter_substitution/single_element_compression.inp'
    Copy("build/tutorial_05_parameter_substitution/amplitudes.inp", "eabm_package/abaqus/amplitudes.inp")
    Copy("build/tutorial_05_parameter_substitution/assembly.inp", "eabm_package/abaqus/assembly.inp")
    Copy("build/tutorial_05_parameter_substitution/boundary.inp", "eabm_package/abaqus/boundary.inp")
    Copy("build/tutorial_05_parameter_substitution/field_output.inp", "eabm_package/abaqus/field_output.inp")
    Copy("build/tutorial_05_parameter_substitution/materials.inp", "eabm_package/abaqus/materials.inp")
    Copy("build/tutorial_05_parameter_substitution/parts.inp", "eabm_package/abaqus/parts.inp")
    Copy("build/tutorial_05_parameter_substitution/history_output.inp", "eabm_package/abaqus/history_output.inp")
    cd /home/roppenheimer/waves-eabm-tutorial/build/tutorial_05_parameter_substitution && /apps/abaqus/Commands/abaqus -information
    environment > single_element_compression_DATACHECK.abaqus_v6.env
    cd /home/roppenheimer/waves-eabm-tutorial/build/tutorial_05_parameter_substitution && /apps/abaqus/Commands/abaqus -job
    single_element_compression_DATACHECK -input single_element_compression -double both -datacheck -interactive -ask_delete
    no > single_element_compression_DATACHECK.stdout 2>&1
    cd /home/roppenheimer/waves-eabm-tutorial/build/tutorial_05_parameter_substitution && ! grep -iE "error"
    single_element_compression_DATACHECK.stdout
    cd /home/roppenheimer/waves-eabm-tutorial/build/tutorial_05_parameter_substitution && /apps/abaqus/Commands/abaqus -information
    environment > single_element_compression.abaqus_v6.env
    cd /home/roppenheimer/waves-eabm-tutorial/build/tutorial_05_parameter_substitution && /apps/abaqus/Commands/abaqus -job
    single_element_compression -input single_element_compression -double both -interactive -ask_delete no >
    single_element_compression.stdout 2>&1
    cd /home/roppenheimer/waves-eabm-tutorial/build/tutorial_05_parameter_substitution && ! grep -iE "error"
    single_element_compression.stdout
    scons: done building targets.

.. _tutorial_parameter_substitution_waves_output_files:

************
Output Files
************

Explore the contents of the ``build`` directory using the ``tree`` command against the ``build`` directory, as shown
below. Note the usage of the ``-I`` option to reduce clutter in the ``tree`` command output.

.. code-block:: bash

    $ pwd
    /home/roppenheimer/waves-eabm-tutorial
    $ tree build/ -I 'tutorial_0[1,2,3,4]*'
    build/
    ├── docs
    │   └── SConscript
    └── tutorial_05_parameter_substitution
        ├── abaqus.rpy
        ├── abaqus.rpy.1
        ├── abaqus.rpy.2
        ├── amplitudes.inp
        ├── assembly.inp
        ├── boundary.inp
        ├── field_output.inp
        ├── history_output.inp
        ├── materials.inp
        ├── parts.inp
        ├── single_element_compression.abaqus_v6.env
        ├── single_element_compression.com
        ├── single_element_compression.dat
        ├── single_element_compression_DATACHECK.023
        ├── single_element_compression_DATACHECK.abaqus_v6.env
        ├── single_element_compression_DATACHECK.com
        ├── single_element_compression_DATACHECK.dat
        ├── single_element_compression_DATACHECK.mdl
        ├── single_element_compression_DATACHECK.msg
        ├── single_element_compression_DATACHECK.odb
        ├── single_element_compression_DATACHECK.par
        ├── single_element_compression_DATACHECK.pes
        ├── single_element_compression_DATACHECK.pmg
        ├── single_element_compression_DATACHECK.prt
        ├── single_element_compression_DATACHECK.sim
        ├── single_element_compression_DATACHECK.stdout
        ├── single_element_compression_DATACHECK.stt
        ├── single_element_compression.inp
        ├── single_element_compression.inp.in
        ├── single_element_compression.msg
        ├── single_element_compression.odb
        ├── single_element_compression.par
        ├── single_element_compression.pes
        ├── single_element_compression.pmg
        ├── single_element_compression.prt
        ├── single_element_compression.sta
        ├── single_element_compression.stdout
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

    2 directories, 51 files

The output files for this tutorial are very similar to those from :ref:`tutorial_simulation_waves` with a few key
differences.

Most importantly, note that the build directory contains a file named ``single_element_compression.inp.in``, which is
the file we created earlier in this tutorial. There is also a file named ``single_element_compression.inp``.

12. Investigate the contents of ``single_element_compression.inp`` using your preferred text editor. Specifically, look
    near the beginning of the file where we defined the ``displacement`` parameter. You should see the following:

.. code-block:: text
   :linenos:
   :emphasize-lines: 6

   **
   *HEADING
   Compressing a single element
   **
   *PARAMETER
   displacement = float('-1.0')
   **

With the use of the :meth:`waves.builders.copy_substitute` builder, we used the ``single_element_compression.inp.in``
file as the source and the ``single_element_compression.inp`` file was the target. The builder acted by substituting the
parameter key ``@displacement@`` with the parameter value ``-1.0``, and then generated the target with this information
in the text, as shown above.

It is also worth noting that that there are 51 files in the ``build/tutorial_05_parameter_substitution`` directory
compared to the 44 files from :ref:`tutorial_simulation_waves`. Other than the addition of the
``single_element_compression.inp.in`` file, the difference is the addition of the files with ``.par``, ``.pes``, and
``.pmg`` extension. See the `Abaqus File Extension Definitions`_ documentation for more information about the
information that these files provide.
