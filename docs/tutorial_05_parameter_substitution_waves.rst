.. _tutorial_parameter_substitution_waves:

###################################
Tutorial 05: Parameter Substitution
###################################

**********
References
**********

* `SCons Substfile`_ :cite:`scons-user`
* `SCons`_ Variable Substitution :cite:`scons-man`


The relevant portion of the `SCons`_ documentation can't be hyperlinked directly. Instead, the relevant portion of the
"Substitution Variables" and "Substitution: Special Variables" sections of the man page is quoted below :cite:`scons-man`.

   Before executing a command, scons performs parameter expansion (substitution) on the string that makes up the action
   part of the builder. The format of a substitutable parameter is ``${expression}``. If ``expression`` refers to a
   variable, the braces in ``${expression}`` can be omitted unless the variable name is immediately followed by a
   character that could either be interpreted as part of the name, or is Python syntax such as ``[`` (for
   indexing/slicing) or ``.`` (for attribute access - see Special Attributes below).

   If ``expression`` refers to a construction variable, it is replaced with the value of that variable in the
   construction environment at the time of execution. If ``expression`` looks like a variable name but is not defined in
   the construction environment it is replaced with an empty string. If ``expression`` refers to one of the Special
   Variables (see below) the corresponding value of the variable is substituted. ``expression`` may also be a Python
   expression to be evaluated. See Python Code Substitution below for a description.

   ...

   Besides regular construction variables, scons provides the following Special Variables for use in expanding commands:

   ...

   ``$SOURCE``

      The file name of the source of the build command, or the file name of the first source if multiple sources are being built.

   ``$SOURCES``

      The file names of the sources of the build command.

   ``$TARGET``

      The file name of the target being built, or the file name of the first target if multiple targets are being built.

   ``$TARGETS``

      The file names of all targets being built.

   These names are reserved and may not be assigned to or used as construction variables. SCons computes them in a
   context-dependent manner and they and are not retrieved from a construction environment.


***********
Environment
***********

.. include:: tutorial_environment_activation.txt

*******************
Directory Structure
*******************

3. Copy the ``tutorial_04_simulation`` file to a new file named ``tutorial_05_parameter_substitution``

.. code-block:: bash

   $ pwd
   /path/to/waves-tutorials
   $ cp tutorial_04_simulation tutorial_05_parameter_substitution

******************
Solver Input Files
******************

4. Copy the ``eabm_package/abaqus/rectangle_compression.inp`` file and all of its contents to a new file in the
   same directory named ``rectangle_compression.inp.in``. **Note:** the only change in the file name is the
   addition of the ``.in`` suffix.

.. code-block:: bash

   $ pwd
   /path/to/waves-tutorials
   $ cp eabm_package/abaqus/rectangle_compression.inp eabm_package/abaqus/rectangle_compression.inp.in

In this tutorial, we will be modifying several files from :ref:`tutorial_simulation_waves`, the first of which is
``rectangle_compression.inp``. We copy this file and all of its contents to a new file with the same basename and
the ``.in`` extension for the purposes of *parameter substitution*. This change is made so it is easy for the
:meth:`waves.scons.copy_substitute` method to identify which files should be searched for parameters. Any files with
the ``.in`` extension that are passed to the :meth:`waves.scons.copy_substitute` method will be parsed for
characters matching the parameter definitions using substitution with `SCons Substfile`_. This is discussed in
more detail later in this tutorial.

5. Use the ``diff`` below to modify your ``rectangle_compression.inp.in`` file.

.. admonition:: waves-tutorials/eabm_package/abaqus/rectangle_compression.inp.in

   .. literalinclude:: abaqus_rectangle_compression.inp.in
      :language: text
      :diff: abaqus_rectangle_compression.inp

The modification made to the ``rectangle_compression.inp.in`` file is to replace the hardcoded displacement value
of ``-1.0`` with the parameter substitution key ``@displacement@``. Note that the `SCons Substfile`_ builder performs a
literal string substitution in the target file, so it is necessary to prepare the correct syntax for the file type where
the substitution occurs.

.. _tutorials_tutorial_parameter_substitution_waves:

**********
SConscript
**********

6. Modify your ``tutorial_05_parameter_substitution`` file by adding the contents shown below to the code
   pertaining to ``# Simulation variables``. The entire code snippet shows how your code should look after editing, and
   the highlghted portion is what needs to be added to your existing code.

.. admonition:: waves-tutorials/tutorial_05_parameter_substitution

   .. literalinclude:: tutorials_tutorial_05_parameter_substitution
      :language: Python
      :lineno-match:
      :start-after: marker-0
      :end-before: marker-1
      :emphasize-lines: 5-10

In the code you just added, a ``simulation_variables`` dictionary is defined.  Each key-value pair in the
``simulation_variables`` dictionary defines a parameter that already exists in several of the scripts we have utilized
in the previous tutorials. The ``width`` and ``height`` parameters are used in the ``rectangle_geometry.py`` and
``rectangle_partition.py`` scripts, and ``global_seed`` is used in the ``rectangle_mesh.py`` script. Recall
that each of these scripts is called using a command line interface that has default parameters. See the
:ref:`waves_eabm_cli` to see what the default values are. As mentioned in :ref:`tutorial_geometry_waves`, the argument
parser for each of these scripts will supply a default value for each command line argument that is not specified
(assuming a defualt value was specified in the argument parser definition).  This allowed us to simplify the command
passed to the :meth:`waves.scons.abaqus_journal` builder. The advantage to coding this behavior ahead of time is that
we get parameter substitution into our journal files when we need it. The ``width``, ``height``, and ``global_seed``
keys of the ``simulation_variables`` dictionary will be used later in this tutorial to specify the values passed to the
journal files via the CLI.

The final key-value pair defined in the ``simulation_variables`` dictionary is ``displacement``. This parameter will be
used in a slightly different way than the others, as the script that utilizes this parameter does not function with a
command line interface. Recall from earlier in this tutorial, we created a new file called
``rectangle_compression.inp.in`` and added the ``@displacement@`` key.  This text file parameter substitution is
the primary reason the ``@`` characters are required in the ``simulation_variables`` keys.  Disussion of exactly how
this is implemented with the :meth:`waves.scons.copy_substitute` method will come later in this tutorial.

7. Modify your ``tutorial_05_parameter_substitution`` file by using the highlighed lines below to modify the
   ``journal_options`` for the code pertaining to ``# Geometry``, ``# Partition``, and ``# Mesh``.

.. admonition:: waves-tutorials/tutorial_05_parameter_substitution

   .. literalinclude:: tutorials_tutorial_05_parameter_substitution
      :language: Python
      :lineno-match:
      :start-after: marker-1
      :end-before: marker-3
      :emphasize-lines: 7, 11-13, 19, 23-25, 29, 33-34

As was previously discussed, we use the key-value pairs of the ``simulation_variables`` dictionary in the arguments we
pass to the command line interfaces for ``rectangle_{geometry,partition,mesh}.py``. Using SCons variable
substitution as shown in the first highlighted section, we will end up passing a string that looks like the following to
the ``rectangle_geometry.py`` CLI:

.. code-block:: python

   --width 1.0 --height 1.0

Note that the keyword arguments ``journal_options``, ``width``, ``height``, and ``global_options`` are not part of the
normal builder interface. `SCons`_ will accept these keyword arguments and use them as substitution variables as part of
the task definition. We can use this feature to pass arbitrary variables to the builder task construction on a per-task
basis without affecting other tasks which use the same builder. For instance, the ``# Mesh`` task will not have access
to the ``width`` and ``height`` substitutions because we have not specified those keyword arguments.

This behavior is repeated for the code pertaining to ``# Partition`` and ``# Mesh``. `SCons`_ will save a signature of
the completed action string as part of the task definition. If the substituted parameter values change, `SCons`_ will
recognize that the tasks need to be re-executed in the same way that tasks need to be re-executed when the contents of a
source file change.

8. Modify your ``tutorial_05_parameter_substitution`` file by using the highlighed lines below to modify the
   code pertaining to ``# SolverPrep``.

.. admonition:: waves-tutorials/tutorial_05_parameter_substitution

   .. literalinclude:: tutorials_tutorial_05_parameter_substitution
      :language: Python
      :lineno-match:
      :start-after: marker-3
      :end-before: marker-4
      :emphasize-lines: 3, 13-15

Per the changes you made earlier in this tutorial, the ``abaqus_source_list`` must be updated to reflect the replacement
of ``rectangle_compression.inp`` with the parameterized ``rectangle_compression.inp.in`` file.

The final change to be made in the ``tutorial_05_parameter_substitution`` file is to utilize the
``substitution_dictionary`` parameter in the usage of the :meth:`waves.scons.copy_substitute` method.

In this tutorial, we leverage two different builder behaviors when defining sources and targets for the
:meth:`waves.scons.copy_substitute` method. We are already familiar with one behavior, where the builder simply
copies the source file to the build directory.

This builder uses template substitution with files named with the ``*.in`` extension, and looks to match and replace
*any characters* that match the keys in the provided ``substitution_dictionary``. For this reason, we must make our
parameter names uniquely identifiable (e.g. ``@variable@``). The surrounding ``@`` character is used during template
subsitution of text files and helps uniquely identify text for parameter substitution without accidentally changing text
that is not a parameter. The matching simulation parameter dictionary key modification is made by the
:meth:`waves.scons.substitution_syntax` method only when necesssary for the ``substitution_dictionary`` behavior to
avoid carrying around the special character for other uses of the simulation variables dictionary.

The second behavior is utilized when we specify a file with ``*.in`` extension in the ``abaqus_source_list`` and we
specify a ``substitution_dictionary`` in the builder's options. This behavior will act on any file in the source list
with ``.in`` extension and attempts to match the parameter keys in the ``substitution_dictionary`` with the text in the
file. For this reason, we must make our parameter names identifiable with a templating character (e.g. ``@variable@``).
In this process, the files with ``.in`` extension are not modified, but are first copied to a file of the same name in
the build directory. The contents of the newly copied file are modified to reflect the parameter substitution and the
``.in`` extension is removed as a default behavior of the `SCons Substfile`_ method. The two step copy/substitute
behavior is required to allow SCons to unambiguously resolve the source-target file locations. We will see this behavior
more clearly when we investigate the :ref:`tutorial_parameter_substitution_waves_output_files` for this tutorial. The
``substitution`` dictionary becomes part of the task signature for all ``*.in`` files. When the dictionary changes,
the copy and substitute operations will be re-executed.

In summary of the changes you just made to the ``tutorial_05_parameter_substitution`` file, a ``diff`` against the
``SConscript`` file from :ref:`tutorial_simulation_waves` is included below to help identify the
changes made in this tutorial.

.. admonition:: waves-tutorials/tutorial_05_parameter_substitution

   .. literalinclude:: tutorials_tutorial_05_parameter_substitution
      :language: Python
      :diff: tutorials_tutorial_04_simulation

**********
SConstruct
**********

9. Add ``tutorial_05_parameter_substitution`` to the ``workflow_configurations`` list in the
    ``waves-tutorials/SConstruct`` file.

A ``diff`` against the ``SConstruct`` file from :ref:`tutorial_simulation_waves` is included below to help identify the
changes made in this tutorial.

.. admonition:: waves-tutorials/SConstruct

   .. literalinclude:: tutorials_tutorial_05_parameter_substitution_SConstruct
      :language: Python
      :diff: tutorials_tutorial_04_simulation_SConstruct

A previous tutorial constructed the ``simulation_variables`` and the ``substitution_dictionary`` variables. The
``simulation_variables`` dictionary is used to define simulation parameters for SCons project configuration and script
command line interfaces. The ``substitution_dictionary`` is constructed from the ``simulation_variables`` dictionary to
apply the parameter substitution syntax (leading and trailing ``@`` character) to each variable name for use with the
``copy_substitute`` method as introduced in the current tutorial.

*************
Build Targets
*************

10. Build the new targets

.. code-block:: bash

    $ pwd
    /path/to/waves-tutorials
    $ scons tutorial_05_parameter_substitution
    scons: Reading SConscript files ...
    Checking whether /apps/abaqus/Commands/abq2023 program exists.../apps/abaqus/Commands/abq2023
    Checking whether abq2023 program exists.../apps/abaqus/Commands/abq2023
    scons: done reading SConscript files.
    scons: Building targets ...
    cd /home/roppenheimer/waves-tutorials/build/tutorial_05_parameter_substitution && /apps/abaqus/Commands/abq2023 -information
    environment > rectangle_geometry.abaqus_v6.env
    cd /home/roppenheimer/waves-tutorials/build/tutorial_05_parameter_substitution && /apps/abaqus/Commands/abq2023 cae -noGui
    /home/roppenheimer/waves-tutorials/eabm_package/abaqus/rectangle_geometry.py -- --width 1.0 --height 1.0 >
    rectangle_geometry.stdout 2>&1
    cd /home/roppenheimer/waves-tutorials/build/tutorial_05_parameter_substitution && /apps/abaqus/Commands/abq2023 -information
    environment > rectangle_partition.abaqus_v6.env
    cd /home/roppenheimer/waves-tutorials/build/tutorial_05_parameter_substitution && /apps/abaqus/Commands/abq2023 cae -noGui
    /home/roppenheimer/waves-tutorials/eabm_package/abaqus/rectangle_partition.py -- --width 1.0 --height 1.0 >
    rectangle_partition.stdout 2>&1
    cd /home/roppenheimer/waves-tutorials/build/tutorial_05_parameter_substitution && /apps/abaqus/Commands/abq2023 -information
    environment > rectangle_mesh.abaqus_v6.env
    cd /home/roppenheimer/waves-tutorials/build/tutorial_05_parameter_substitution && /apps/abaqus/Commands/abq2023 cae -noGui
    /home/roppenheimer/waves-tutorials/eabm_package/abaqus/rectangle_mesh.py -- --global-seed 1.0 >
    rectangle_mesh.stdout 2>&1
    Copy("build/tutorial_05_parameter_substitution/rectangle_compression.inp.in",
    "eabm_package/abaqus/rectangle_compression.inp.in")
    Creating 'build/tutorial_05_parameter_substitution/rectangle_compression.inp'
    Copy("build/tutorial_05_parameter_substitution/assembly.inp", "eabm_package/abaqus/assembly.inp")
    Copy("build/tutorial_05_parameter_substitution/boundary.inp", "eabm_package/abaqus/boundary.inp")
    Copy("build/tutorial_05_parameter_substitution/field_output.inp", "eabm_package/abaqus/field_output.inp")
    Copy("build/tutorial_05_parameter_substitution/materials.inp", "eabm_package/abaqus/materials.inp")
    Copy("build/tutorial_05_parameter_substitution/parts.inp", "eabm_package/abaqus/parts.inp")
    Copy("build/tutorial_05_parameter_substitution/history_output.inp", "eabm_package/abaqus/history_output.inp")
    cd /home/roppenheimer/waves-tutorials/build/tutorial_05_parameter_substitution && /apps/abaqus/Commands/abq2023 -information
    environment > rectangle_compression.abaqus_v6.env
    cd /home/roppenheimer/waves-tutorials/build/tutorial_05_parameter_substitution && /apps/abaqus/Commands/abq2023 -job
    rectangle_compression -input rectangle_compression -double both -interactive -ask_delete no >
    rectangle_compression.stdout 2>&1
    scons: done building targets.

.. _tutorial_parameter_substitution_waves_output_files:

************
Output Files
************

Explore the contents of the ``build`` directory using the ``tree`` command against the ``build`` directory, as shown
below. Note the usage of the ``-I`` option to reduce clutter in the ``tree`` command output.

.. code-block:: bash

   $ pwd
   /home/roppenheimer/waves-tutorials
   $ tree build/tutorial_05_parameter_substitution
   build/tutorial_05_parameter_substitution
   |-- abaqus.rpy
   |-- abaqus.rpy.1
   |-- abaqus.rpy.2
   |-- assembly.inp
   |-- boundary.inp
   |-- field_output.inp
   |-- history_output.inp
   |-- materials.inp
   |-- parts.inp
   |-- rectangle_compression.abaqus_v6.env
   |-- rectangle_compression.com
   |-- rectangle_compression.dat
   |-- rectangle_compression.inp
   |-- rectangle_compression.inp.in
   |-- rectangle_compression.msg
   |-- rectangle_compression.odb
   |-- rectangle_compression.prt
   |-- rectangle_compression.sta
   |-- rectangle_compression.stdout
   |-- rectangle_geometry.abaqus_v6.env
   |-- rectangle_geometry.cae
   |-- rectangle_geometry.jnl
   |-- rectangle_geometry.stdout
   |-- rectangle_mesh.abaqus_v6.env
   |-- rectangle_mesh.cae
   |-- rectangle_mesh.inp
   |-- rectangle_mesh.jnl
   |-- rectangle_mesh.stdout
   |-- rectangle_partition.abaqus_v6.env
   |-- rectangle_partition.cae
   |-- rectangle_partition.jnl
   `-- rectangle_partition.stdout

   0 directories, 32 files

The output files for this tutorial are very similar to those from :ref:`tutorial_simulation_waves` with a few key
differences.

Most importantly, note that the build directory contains a file named ``rectangle_compression.inp.in``, which is
the file we created earlier in this tutorial. There is also a file named ``rectangle_compression.inp``.

11. Investigate the contents of ``rectangle_compression.inp`` using your preferred text editor. Specifically, look
    in the step definition where we defined the ``displacement`` parameter. You should see the following:

.. code-block:: text
   :linenos:
   :emphasize-lines: 6

   *STEP, NLGEOM=NO, INC=100, AMPLITUDE=RAMP
   *STATIC
   .005, 1.00, 0.000001, 0.5
   **
   *BOUNDARY,OP=MOD
   A.rectangle.top,2,2,-0.01
   **

With the use of the :meth:`waves.scons.copy_substitute` method, we used the ``rectangle_compression.inp.in``
file as the source and the ``rectangle_compression.inp`` file was the target. The builder acted by substituting the
parameter key ``@displacement@`` with the parameter value ``-1.0``, and then generated the target with this information
in the text, as shown above.

It is also worth noting that that there are 50 files in the ``build/tutorial_05_parameter_substitution`` directory
compared to the 43 files from :ref:`tutorial_simulation_waves`. Other than the addition of the
``rectangle_compression.inp.in`` file, the difference is the addition of the files with ``.par``, ``.pes``, and
``.pmg`` extension. See the `Abaqus File Extension Definitions`_ documentation :cite:`ABAQUS` for more information
about the information that these files provide.

**********************
Workflow Visualization
**********************

View the workflow directed graph by running the following command and opening the image in your preferred image viewer.

.. code-block::

   $ pwd
   /home/roppenheimer/waves-tutorials
   $ waves visualize tutorial_05_parameter_substitution --output-file tutorial_05_parameter_substitution.png --width=28 --height=6 --exclude-list /usr/bin .stdout .jnl .env .prt .com

The output should look similar to the figure below.

.. raw:: latex

    \begin{landscape}
        \vspace*{\fill}

.. figure:: tutorial_05_parameter_substitution.png
   :align: center

.. raw:: latex

        \vspace*{\fill}
    \end{landscape}
