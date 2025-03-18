.. _tutorial_parameter_substitution:

###################################
Tutorial 05: Parameter Substitution
###################################

**********
References
**********

* `SCons Substfile`_ :cite:`scons-user`
* `SCons Variable Substitution`_  :cite:`scons-man`
* `SCons Special Variables`_ :cite:`scons-man`

***********
Environment
***********

.. include:: tutorial_environment_activation.txt

.. include:: version_check_warning.txt

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

4. Download and copy the ``tutorial_04_simulation`` file to a new file named ``tutorial_05_parameter_substitution``
   with the :ref:`waves_cli` :ref:`waves_fetch_cli` subcommand.

.. code-block:: bash

   $ pwd
   /home/roppenheimer/waves-tutorials
   $ waves fetch --overwrite tutorials/tutorial_04_simulation && cp tutorial_04_simulation tutorial_05_parameter_substitution
   WAVES fetch
   Destination directory: '/home/roppenheimer/waves-tutorials'

******************
Solver Input Files
******************

5. Copy the ``modsim_package/abaqus/rectangle_compression.inp`` file and all of its contents to a new file in the
   same directory named ``rectangle_compression.inp.in``. **Note:** the only change in the file name is the
   addition of the ``.in`` suffix.

.. code-block:: bash

   $ pwd
   /home/roppenheimer/waves-tutorials
   $ cp modsim_package/abaqus/rectangle_compression.inp modsim_package/abaqus/rectangle_compression.inp.in

In this tutorial, we will be modifying several files from :ref:`tutorial_simulation`, the first of which is
``rectangle_compression.inp``. We copy this file and all of its contents to a new file with the same basename and
the ``.in`` extension for the purposes of *parameter substitution*. This change is made so it is easy for the
:meth:`waves.scons_extensions.copy_substfile` method to identify which files should be searched for parameters. Any files with
the ``.in`` extension that are passed to the :meth:`waves.scons_extensions.copy_substfile` method will be parsed for
characters matching the parameter definitions using substitution with `SCons Substfile`_. This is discussed in
more detail later in this tutorial.

6. Use the ``diff`` below to modify your ``rectangle_compression.inp.in`` file.

.. admonition:: waves-tutorials/modsim_package/abaqus/rectangle_compression.inp.in

   .. literalinclude:: abaqus_rectangle_compression.inp.in
      :language: text
      :diff: abaqus_rectangle_compression.inp

The modification made to the ``rectangle_compression.inp.in`` file is to replace the hardcoded displacement value
of ``-1.0`` with the parameter substitution key ``@displacement@``. Note that the `SCons Substfile`_ builder performs a
literal string substitution in the target file, so it is necessary to prepare the correct syntax for the file type where
the substitution occurs.

.. _tutorials_tutorial_parameter_substitution:

**********
SConscript
**********

7. Modify your ``tutorial_05_parameter_substitution`` file by adding the contents shown below to the code
   pertaining to ``# Simulation variables``. The entire code snippet shows how your code should look after editing, and
   the highlghted portion is what needs to be added to your existing code.

.. admonition:: waves-tutorials/tutorial_05_parameter_substitution

   .. literalinclude:: tutorials_tutorial_05_parameter_substitution
      :language: Python
      :lineno-match:
      :start-after: marker-0
      :end-before: marker-1
      :emphasize-lines: 4-10

In the code you just added, a ``simulation_variables`` dictionary is defined.  Each key-value pair in the
``simulation_variables`` dictionary defines a parameter that already exists in several of the scripts we have utilized
in the previous tutorials. The ``width`` and ``height`` parameters are used in the ``rectangle_geometry.py`` and
``rectangle_partition.py`` scripts, and ``global_seed`` is used in the ``rectangle_mesh.py`` script. Recall
that each of these scripts is called using a command-line interface that has default parameters. See the
:ref:`waves_tutorial_cli` to see what the default values are. As mentioned in :ref:`tutorial_geometry`, the argument
parser for each of these scripts will supply a default value for each command-line argument that is not specified
(assuming a defualt value was specified in the argument parser definition).  This allowed us to simplify the command
passed to the :meth:`waves.scons_extensions.abaqus_journal_builder_factory` builder. The advantage to coding this behavior ahead of time is that
we get parameter substitution into our journal files when we need it. The ``width``, ``height``, and ``global_seed``
keys of the ``simulation_variables`` dictionary will be used later in this tutorial to specify the values passed to the
journal files via the CLI.

The final key-value pair defined in the ``simulation_variables`` dictionary is ``displacement``. This parameter will be
used in a slightly different way than the others, as the script that utilizes this parameter does not function with a
command-line interface. Recall from earlier in this tutorial, we created a new file called
``rectangle_compression.inp.in`` and added the ``@displacement@`` key.  This text file parameter substitution is
the primary reason the ``@`` characters are required in the ``simulation_variables`` keys.  Disussion of exactly how
this is implemented with the :meth:`waves.scons_extensions.copy_substfile` method will come later in this tutorial.

8. Modify your ``tutorial_05_parameter_substitution`` file by using the highlighed lines below to modify the
   ``subcommand_options`` for the code pertaining to ``# Geometry``, ``# Partition``, and ``# Mesh``.

.. admonition:: waves-tutorials/tutorial_05_parameter_substitution

   .. literalinclude:: tutorials_tutorial_05_parameter_substitution
      :language: Python
      :lineno-match:
      :start-after: marker-1
      :end-before: marker-3
      :emphasize-lines: 10-11, 22-23, 32-33

As was previously discussed, we use the key-value pairs of the ``simulation_variables`` dictionary in the arguments we
pass to the command-line interfaces for ``rectangle_{geometry,partition,mesh}.py``. Using SCons variable
substitution as shown in the first highlighted section, we will end up passing a string that looks like the following to
the ``rectangle_geometry.py`` CLI:

.. code-block:: python

   --width 1.0 --height 1.0

Note that the keyword arguments ``subcommand_options``, ``width``, ``height``, and ``global_options`` are not part of the
normal builder interface. `SCons`_ will accept these keyword arguments and use them as substitution variables as part of
the task definition. We can use this feature to pass arbitrary variables to the builder task construction on a per-task
basis without affecting other tasks which use the same builder. For instance, the ``# Mesh`` task will not have access
to the ``width`` and ``height`` substitutions because we have not specified those keyword arguments.

This behavior is repeated for the code pertaining to ``# Partition`` and ``# Mesh``. `SCons`_ will save a signature of
the completed action string as part of the task definition. If the substituted parameter values change, `SCons`_ will
recognize that the tasks need to be re-executed in the same way that tasks need to be re-executed when the contents of a
source file change.

9. Modify your ``tutorial_05_parameter_substitution`` file by using the highlighed lines below to modify the
   code pertaining to ``# SolverPrep``.

.. admonition:: waves-tutorials/tutorial_05_parameter_substitution

   .. literalinclude:: tutorials_tutorial_05_parameter_substitution
      :language: Python
      :lineno-match:
      :start-after: marker-3
      :end-before: marker-4
      :emphasize-lines: 3, 14

Per the changes you made earlier in this tutorial, the ``abaqus_source_list`` must be updated to reflect the replacement
of ``rectangle_compression.inp`` with the parameterized ``rectangle_compression.inp.in`` file.

The final change to be made in the ``tutorial_05_parameter_substitution`` file is to utilize the
``substitution_dictionary`` parameter in the usage of the :meth:`waves.scons_extensions.copy_substfile` method.

In this tutorial, we leverage two different builder behaviors when defining sources and targets for the
:meth:`waves.scons_extensions.copy_substfile` method. We are already familiar with one behavior, where the builder
simply copies the source file to the build directory.

The second behavior is to apply template substitution on files with the ``*.in`` extension in the ``abaqus_source_list``
using a ``substitution_dictionary`` provided in the builder's options. The builder will search any file with the ``.in``
extension for strings matching ``substitution_dictionary`` parameter keys. Any key found in the file's text will be
replaced with the corresponding ``substitution_dictionary`` value. To avoid spurious text replacements on text unrelated
to our parameters, we must make our parameter names uniquely identifiable with a templating character (e.g.
``@variable@``). To avoid carrying around two copies of the simulation variables dictionary, one with the special
characters and one without, the :meth:`waves.scons_extensions.substitution_syntax` method can be used to modify the
simulation variable dictionary keys as needed.

In this template substitution process, the files with ``.in`` are first copied to a file of the same name in the build
directory. The contents of the newly copied file are modified to reflect the parameter substitution and the ``.in``
extension is removed as a default behavior of the `SCons Substfile`_ method. The two step copy/substitute behavior is
required to allow SCons to unambiguously resolve the source-target file locations. We will see this behavior more
clearly when we investigate the :ref:`tutorial_parameter_substitution_waves_output_files` for this tutorial. The
``substitution`` dictionary becomes part of the task signature for all ``*.in`` files. When the dictionary changes, the
copy and substitute operations will be re-executed.

In summary of the changes you just made to the ``tutorial_05_parameter_substitution`` file, a ``diff`` against the
``SConscript`` file from :ref:`tutorial_simulation` is included below to help identify the
changes made in this tutorial.

.. admonition:: waves-tutorials/tutorial_05_parameter_substitution

   .. literalinclude:: tutorials_tutorial_05_parameter_substitution
      :language: Python
      :diff: tutorials_tutorial_04_simulation

**********
SConstruct
**********

10. Add ``tutorial_05_parameter_substitution`` to the ``workflow_configurations`` list in the
    ``waves-tutorials/SConstruct`` file.

A ``diff`` against the ``SConstruct`` file from :ref:`tutorial_simulation` is included below to help identify the
changes made in this tutorial.

.. admonition:: waves-tutorials/SConstruct

   .. literalinclude:: tutorials_tutorial_05_parameter_substitution_SConstruct
      :language: Python
      :diff: tutorials_tutorial_04_simulation_SConstruct

A previous tutorial constructed the ``simulation_variables`` and the ``substitution_dictionary`` variables. The
``simulation_variables`` dictionary is used to define simulation parameters for SCons project configuration and script
command-line interfaces. The ``substitution_dictionary`` is constructed from the ``simulation_variables`` dictionary to
apply the parameter substitution syntax (leading and trailing ``@`` character) to each variable name for use with the
``copy_substfile`` method as introduced in the current tutorial.

*************
Build Targets
*************

11. Build the new targets

.. code-block:: bash

    $ pwd
    /home/roppenheimer/waves-tutorials
    $ scons tutorial_05_parameter_substitution
    scons: Reading SConscript files ...
    Checking whether /apps/abaqus/Commands/abq2024 program exists.../apps/abaqus/Commands/abq2024
    Checking whether abq2024 program exists.../apps/abaqus/Commands/abq2024
    scons: done reading SConscript files.
    scons: Building targets ...
    cd /home/roppenheimer/waves-tutorials/build/tutorial_05_parameter_substitution && /apps/abaqus/Commands/abq2024 cae -noGui /home/roppenheimer/waves-tutorials/modsim_package/abaqus/rectangle_geometry.py -- --width 1.0 --height 1.0 > rectangle_geometry.stdout 2>&1
    cd /home/roppenheimer/waves-tutorials/build/tutorial_05_parameter_substitution && /apps/abaqus/Commands/abq2024 cae -noGui /home/roppenheimer/waves-tutorials/modsim_package/abaqus/rectangle_partition.py -- --width 1.0 --height 1.0 > rectangle_partition.stdout 2>&1
    cd /home/roppenheimer/waves-tutorials/build/tutorial_05_parameter_substitution && /apps/abaqus/Commands/abq2024 cae -noGui /home/roppenheimer/waves-tutorials/modsim_package/abaqus/rectangle_mesh.py -- --global-seed 1.0 > rectangle_mesh.stdout 2>&1
    Copy("build/tutorial_05_parameter_substitution/rectangle_compression.inp.in", "modsim_package/abaqus/rectangle_compression.inp.in")
    Creating 'build/tutorial_05_parameter_substitution/rectangle_compression.inp'
    Copy("build/tutorial_05_parameter_substitution/assembly.inp", "modsim_package/abaqus/assembly.inp")
    Copy("build/tutorial_05_parameter_substitution/boundary.inp", "modsim_package/abaqus/boundary.inp")
    Copy("build/tutorial_05_parameter_substitution/field_output.inp", "modsim_package/abaqus/field_output.inp")
    Copy("build/tutorial_05_parameter_substitution/materials.inp", "modsim_package/abaqus/materials.inp")
    Copy("build/tutorial_05_parameter_substitution/parts.inp", "modsim_package/abaqus/parts.inp")
    Copy("build/tutorial_05_parameter_substitution/history_output.inp", "modsim_package/abaqus/history_output.inp")
    cd /home/roppenheimer/waves-tutorials/build/tutorial_05_parameter_substitution && /apps/abaqus/Commands/abq2024 -job rectangle_compression -input rectangle_compression -double both -interactive -ask_delete no > rectangle_compression.stdout 2>&1
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
   |-- rectangle_compression.com
   |-- rectangle_compression.dat
   |-- rectangle_compression.inp
   |-- rectangle_compression.inp.in
   |-- rectangle_compression.msg
   |-- rectangle_compression.odb
   |-- rectangle_compression.prt
   |-- rectangle_compression.sta
   |-- rectangle_compression.stdout
   |-- rectangle_geometry.cae
   |-- rectangle_geometry.jnl
   |-- rectangle_geometry.stdout
   |-- rectangle_mesh.cae
   |-- rectangle_mesh.inp
   |-- rectangle_mesh.jnl
   |-- rectangle_mesh.stdout
   |-- rectangle_partition.cae
   |-- rectangle_partition.jnl
   `-- rectangle_partition.stdout

   0 directories, 28 files

The output files for this tutorial are very similar to those from :ref:`tutorial_simulation` with a few key
differences.

Most importantly, note that the build directory contains a file named ``rectangle_compression.inp.in``, which is
the file we created earlier in this tutorial. There is also a file named ``rectangle_compression.inp``.

12. Investigate the contents of ``rectangle_compression.inp`` using your preferred text editor. Specifically, look
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

With the use of the :meth:`waves.scons_extensions.copy_substfile` method, we used the ``rectangle_compression.inp.in``
file as the source and the ``rectangle_compression.inp`` file was the target. The builder acted by substituting the
parameter key ``@displacement@`` with the parameter value ``-1.0``, and then generated the target with this information
in the text, as shown above.

It is also worth noting that that there are 29 files in the ``build/tutorial_05_parameter_substitution`` directory
compared to the 28 files from :ref:`tutorial_simulation` with the addition of the
``rectangle_compression.inp.in`` file.

**********************
Workflow Visualization
**********************

View the workflow directed graph by running the following command and opening the image in your preferred image viewer.

.. code-block::

   $ pwd
   /home/roppenheimer/waves-tutorials
   $ waves visualize tutorial_05_parameter_substitution --output-file tutorial_05_parameter_substitution.png --width=36 --height=6 --exclude-list /usr/bin .stdout .jnl .prt .com

The output should look similar to the figure below.

.. raw:: latex

    \begin{landscape}
        \vspace*{\fill}

.. figure:: tutorial_05_parameter_substitution.png
   :align: center
   :width: 100%

.. raw:: latex

        \vspace*{\fill}
    \end{landscape}
