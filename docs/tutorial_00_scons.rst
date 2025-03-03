.. _tutorialsconstruct:

#######################
Tutorial 00: SConstruct
#######################

*************
Prerequisites
*************

.. include:: tutorial_00_prerequisites.txt

**********
References
**********

* Python style guide: `PEP-8`_ :cite:`pep-8`

.. _sconstruct_environment:

***********
Environment
***********

.. include:: tutorial_environment_activation.txt

.. include:: version_check_warning.txt

***********
Description
***********

`WAVES`_ is a suite of build wrappers and command-line utilities for the build system `SCons`_. Build systems help
automate the execution of complex computing workflows by constructing component task execution order. In the
`WAVES tutorials`_ there are two components to the `SCons`_ project configuration: project configuration and
simulation workflow configurations. This tutorial introduces the `SCons`_ project configuration file for the
`WAVES tutorials`_ and :ref:`modsim_templates`.

The command-line utilities provided by `WAVES`_ are those utilities required to implement engineering workflows in
traditional software build systems. For most engineering simulation workflows, software build systems will work
out-of-the-box. However, it is difficult to implement engineering parameter studies in software build systems, which are
designed to produce a single program, not many nearly identical configurations of the same program. The `WAVES`_
parameter generator command-line interface(s) is designed to work with most build systems, but were originally developed
with the requirements of `CMake`_ in mind.

For production-engineering analysis, `WAVES`_ focuses on extending the build system `SCons`_ because `SCons`_
configuration files use `Python`_ as a fully featured scripting language. This choice is primarily driven by the
familiarity of the engineering community with `Python`_ as a programming language, but also because the parameter
generation utility can be integrated more closely with the build system via a Python API,
:ref:`parameter_generator_api`.

This tutorial will build out the project configuration file, named ``SConstruct`` by default. First a code snippet will
be introduced followed by a description of what that snippet does. After sufficient code is added to the file, it can be
executed with the ``scons`` command. Later tutorials will continue to expand the SConstruct file and add workflow
configuration files.

***************************
SCons Project Configuration
***************************

.. include:: tutorial_directory_setup.txt

4. Create a new file named ``SConstruct`` in the ``waves-tutorials`` directory and add the contents listed below. Note
   that the filename is case sensitive and does not use a file extension.

.. admonition:: waves-tutorials/SConstruct

   .. literalinclude:: tutorials_tutorial_00_SConstruct
      :language: Python
      :lineno-match:
      :end-before: marker-1

By convention, the `SCons`_ root project file is named ``SConstruct``. Because this is a `Python`_ file, we can import
`Python`_ libraries to help define project settings. The `shebang`_ in the first line is included to help text editors
identify the file as a Python file for syntax highlighting. Using the `PEP-8`_ formatting, the `Python`_ built-in
imports are listed in the first block and third-party imports are listed in the second block, including the `WAVES`_
package.

5. Add the content below to the ``SConstruct`` file to add the project's command-line build options to the project
   configuration.

.. include:: line_number_jump_note.txt

.. admonition:: waves-tutorials/SConstruct

   .. literalinclude:: tutorials_tutorial_00_SConstruct
      :language: Python
      :lineno-match:
      :start-after: marker-1
      :end-before: marker-2

The `SCons command-line build options`_ are specific to the project configuration that you are currently creating.
`SCons`_ projects may add or remove command-line options to aid in build behavior control. The most relevant option to
modsim projects will be ``--build-dir`` and ``--abaqus-command``, which allow project developers to change the build
directory location and Abaqus executable path from the command-line without modifying the ``SConstruct`` file source
code.

For example, when there are workflow tasks defined in the the ``SConstruct`` file, a call to ``scons`` would create the
default build directory named ``build`` and a call to ``scons --build-dir=non_default_build`` would create a build
directory named ``non_default_build``. The current SConstruct file will not produce these directories yet because there
are no workflow tasks defined. The demonstration below shows how the build directory option will behave when workflow
tasks are defined.

.. warning::

   The equals sign separator is important to the internal implementation of options defined by ``AddOption`` in
   SConstruct files. When whitespace is used to delimit the option from the argument, the argument handling is undefined
   and may result in unexpected behavior. Interested readers can read more in the SCons documentation:
   https://scons.org/doc/production/HTML/scons-user.html#app-functions

.. code-block::

   $ scons
   $ ls
   build SConstruct
   $ scons --build-dir=non_default_build
   $ ls
   build non_default_build SConstruct

The ``--abaqus-command`` option will be useful if the tutorial files struggle to find your Abaqus installation. You can
also edit the ``default_abaqus_commands`` list to include your Abaqus installation to avoid having to provide it on the
command line every time you call ``scons``.

.. code-block::

   $ scons --abaqus-command=/path/to/installed/abaqus

The ``--unconditional-build`` option is mostly useful for :ref:`testing` and continuous integration. It is used in the
tutorial workflows to force a workflow to execute, even if the required programs are not found. This is useful for
system testing software availability in the construction environment itself.

By default, |PROJECT| builders redirect task STDOUT and STDERR to a ``*.stdout`` file to avoid cluttering the task
execution reported by SCons.  The ``--print-build-failures`` will print the associated ``*.stdout`` file of all failed
tasks at the end of SCons execution.

At the end of this tutorial, you will see how to explore the project specific command-line options help and usage.

6. Add the content below to the ``SConstruct`` file to initialize the :class:`waves.scons_extensions.WAVESEnvironment`
   `SCons construction environment`_.

.. admonition:: waves-tutorials/SConstruct

   .. literalinclude:: tutorials_tutorial_00_SConstruct
      :language: Python
      :lineno-match:
      :start-after: marker-2
      :end-before: marker-3

Most build systems inherit the user's active `shell environment`_ at build configuration time, referred to as the
"external" environment in the `SCons`_ documentation. This means that (most) of the environment must be identical for
all build tasks in the project. `SCons`_ differs from most build systems by managing the construction environment for
each task separately from the external environment. `SCons`_ projects do not inherit the user's shell environment at
build configuration by default. Instead, projects define one or more construction environments that is used to define
per-task environment configuration.

While this is a powerful feature for large, complex projects, most modsim projects will benefit from maintaining a single
construction environment inherited from the active shell environment at build configuration time. In addition to copying
the active external environment, the above code adds the project command-line build options to the construction
environment for reuse throughout the project configuration files, SConstruct and SConscript, for build control.

7. Add the content below to the ``SConstruct`` file to add the third-party software dependency checks to the project
   configuration.

.. admonition:: waves-tutorials/SConstruct

   .. literalinclude:: tutorials_tutorial_00_SConstruct
      :language: Python
      :lineno-match:
      :start-after: marker-3
      :end-before: marker-4

These checks are not strictly required for an `SCons`_ `WAVES`_ modsim project; however, they provide valuable build
control options for developers. Most of the `WAVES tutorials`_  compute environment dependencies are `Python`_ packages
managed with `Conda`_ as described in the :ref:`sconstruct_environment` section of this tutorial.  Many :term:`modsim
repositories` will also depend on proprietary or commercial software that is not included in a package manager such as
`Conda`_. Instead, the project configuration can check the construction environment for software installation(s) and
provide an environment variable to conditionally skip any tasks that depend on missing software.

In `WAVES`_ and `WAVES tutorials`_, this approach is primarily used to allow developers to perform development work on
local computers without cluttering their test builds with tasks that cannot succeed on their local computer.
:ref:`tutorial_geometry` will introduce the use of these variables for build control.

The `SCons`_ native solution for finding a program is the `CheckProg`_ configuration method. The
:meth:`waves.scons_extensions.add_program` method wraps `CheckProg`_ like behavior to search for a list of possible
program names. This is most useful when multiple versions of a program can be used to build the project and the various
servers where the project is built may have different versions available. The project will build with the first
available program name without changes to the project configuration. If a program is found, it will also be added to the
SCons environment ``PATH``.

The ``env.AddProgram`` was added to the construction environment with :class:`waves.scons_extensions.WAVESEnvironment`
for convenience. Anywhere the construction environment is available, we can use ``env.AddProgram``. It is also possible
to use the :meth:`waves.scons_extensions.add_program` function directly.  Most projects will search for more than one
third-party software, so the shortened ``env.AddProgram`` function call is also less to type.

.. note::

   The Abaqus program naming convention used here is specific to the naming convention used on the `WAVES`_ continuous
   integration server. Users may need to update the abaqus program name to match their system installation.

8. Add the content below to the ``SConstruct`` file to add the project meta data to the construction environment.

.. admonition:: waves-tutorials/SConstruct

   .. literalinclude:: tutorials_tutorial_00_SConstruct
      :language: Python
      :lineno-match:
      :start-after: marker-4
      :end-before: marker-5

The `WAVES tutorials`_ make use of the `SCons hierarchical build`_ feature to separate simulation output in the build
directory. This is valuable for :term:`modsim repositories` that include a suite of simulations. To avoid hardcoded duplication
of project meta data, the project meta data variables are added to the construction environment, which will be passed
around to all `SCons`_ configuration files. The implementation that passes the construction environment around is
introduced in :ref:`tutorial_geometry`.

9. Add the content below to the ``SConstruct`` file to add a placeholder for `WAVES`_ builders to the project
   configuration.

.. admonition:: waves-tutorials/SConstruct

   .. literalinclude:: tutorials_tutorial_00_SConstruct
      :language: Python
      :lineno-match:
      :start-after: marker-5
      :end-before: marker-6

Although it is possible to re-create the `WAVES tutorials`_ entirely in native `SCons`_ code, the builder extensions
provided by `WAVES`_ reduce the requisite background knowledge to begin creating :term:`modsim` repositories. While the
:class:`waves.scons_extensions.WAVESEnvironment` construction environment provides some useful default builders, it is
possible and often valuable to add project custom-tailored builders, as well. The construction environment ``BUILDERS``
variable must be updated to include these custom `SCons`_ builders and make them available to the simulation
configuration starting in :ref:`tutorial_simulation`.

The `WAVES`_ :ref:`waves_scons_api` API describes the available builder factories and their usage. As `WAVES`_ matures,
more software will be supported with build wrappers. Prior to a `WAVES`_ builder, modsim developers can create their own
`SCons custom builders`_ or start from a `WAVES`_ template builder factory in :ref:`tutorial_writing_builders`.

10. Add the content below to the ``SConstruct`` file to create a placeholder call to the hierarchical simulation configuration files.

.. admonition:: waves-tutorials/SConstruct

   .. literalinclude:: tutorials_tutorial_00_SConstruct
      :language: Python
      :lineno-match:
      :start-after: marker-6
      :end-before: marker-7

The for loop in this code-snippet is the method for implementing an `SCons hierarchical build`_. The ``exports`` keyword
argument allows the project configuration file to pass the ``env`` construction environment variable with the `SCons
sharing environments`_ feature. The first simulation configuration will be added to the ``workflow_configurations``
list in :ref:`tutorial_geometry`.

11. Add the content below to the ``SConstruct`` file to add an empty default target list and to modify the project help
    message.

.. admonition:: waves-tutorials/SConstruct

   .. literalinclude:: tutorials_tutorial_00_SConstruct
      :language: Python
      :lineno-match:
      :start-after: marker-7
      :end-before: marker-8

Because the `WAVES tutorials`_ contain a suite of simulations, it is useful to limit what `SCons`_ will build by default. To
protect against running all simulations by default, create an empty default list. This will require that simulation
targets are specified by name in the `SCons`_ build command. In addition to limiting the default target list, it is
useful to print the list of default targets in the project help to remind developers what targets will build when no
target is specified in the call to ``scons``.

Simulation build workflows will typically involve many targets and tasks in a non-trivial execution order. The target
file names may also be cumbersome to type when explicitly listing build targets in the `SCons`_ build command. For
convenience, the `WAVES tutorials`_ simulation configurations will add a collector alias for the list of simulation targets
with the `SCons Alias`_ feature. By convention, the `WAVES tutorials`_ match the alias name to the simulation subdirectory
name. :ref:`tutorial_geometry` will introduce the first target alias, which will then populate the project help
message displayed by the ``scons -h`` command option.

We previously added the ``ProjectHelp`` method to the construction environment using
:class:`waves.scons_extensions.WAVESEnvironment`. This points to :meth:`waves.scons_extensions.project_help`
which wraps two common calls to `SCons Help`_ that will append the following to the project help message accessed by
``scons -h``:

* the command-line build options
* the default target list
* the project alias list

The help message recovers targets and aliases from the construction environment, so the ``env.ProjectHelp`` call must
come after all ``SConscript`` and ``Alias`` method calls.  Generally, it's best to simply call this method as the final
line in your project configuration.

.. note::

   The project help message uses the conventional lowercase help option, ``-h``. Most bash commands use this option to
   display the command's help message corresponding to the software options. Due to this behavior, the `SCons`_ command
   options are displayed with the unconventional capitalized option, ``-H``, as ``scons -H``. The `WAVES tutorials`_ and
   documentation will not discuss the full range of `SCons`_ command options, so modsim developers are encouraged to
   read the `SCons`_ usage summary and `SCons manpage`_ to learn more about available build control options.

12. Explore the project help message

.. code-block::

   $ pwd
   /home/roppenheimer/waves-tutorials
   $ scons -h
   scons: Reading SConscript files ...
   Checking whether /apps/abaqus/Commands/abq2024 program exists.../apps/abaqus/Commands/abq2024
   Checking whether abq2024 program exists.../apps/abaqus/Commands/abq2024
   scons: done reading SConscript files.
   Local Options:
     --build-dir=DIR         SCons build (variant) root directory. Relative or absolute path. (default: 'build')
     --unconditional-build   Boolean flag to force building of conditionally ignored targets, e.g. if the target's
                               action program is missing and it would normally be ignored. (default: 'False')
     --print-build-failures  Print task *.stdout target file(s) on build failures. (default: 'False')

   Default Targets:

   Target Aliases:

   Use scons -H for help about SCons built-in command-line options.

The text shown in the sample code block above is the project specific help message(s) added in the previous step. The
``Default Targets:`` and ``Target Aliases:`` lists will begin to populate in the following tutorial.
