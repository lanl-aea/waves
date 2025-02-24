.. _tutorial_geometry:

#####################
Tutorial 01: Geometry
#####################

*************
Prerequisites
*************

.. include:: tutorial_00_prerequisites.txt

**********
References
**********

Below is a list of references for more information about topics that are not explicitly
covered in this tutorial.

* Python style guide: `PEP-8`_ :cite:`pep-8`
* Python Docstrings: `PEP-257`_, `PEP-287`_
* Python Argparse: `Python 3 argparse`_, `Python 2.7 argparse`_
* `Abaqus Scripting`_ :cite:`ABAQUS`
* `Abaqus Python Environment`_ :cite:`ABAQUS`

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

    .. code-block::

        $ pwd
        /home/roppenheimer/waves-tutorials
        $ waves fetch --overwrite --tutorial 0 && mv tutorial_00_SConstruct SConstruct
        WAVES fetch
        Destination directory: '/home/roppenheimer/waves-tutorials'


4. Within the ``waves-tutorials`` directory, create a new directory called
   ``modsim_package/abaqus``. For example, in a bash shell:

.. code-block::

    $ pwd
    /home/roppenheimer/waves-tutorials
    $ mkdir -p modsim_package/abaqus

5. Create Python module initialization files to create a project specific local Python package.

.. admonition:: waves-tutorials/modsim_package/__init__.py and waves-tutorials/modsim_package/abaqus/__init__.py

   .. code-block::

      $ pwd
      /home/roppenheimer/waves-tutorials
      $ waves fetch tutorials/modsim_package/__init__.py tutorials/modsim_package/abaqus/__init__.py --destination modsim_package
      $ find . -name "__init__.py"
      ./modsim_package/__init__.py
      ./modsim_package/abaqus/__init__.py

***************
SConscript File
***************

An ``SConscript`` file defines sources, actions, and targets. Sources are files that exist in the source
repository, such as Abaqus journal files. Actions define how to process source files, for example executing the Abaqus
command. Targets are the output artifacts created by the action, such as an Abaqus model file. It is also worth noting
that the ``SConscript`` file naming convention is case sensitive. In this tutorial, we will build the geometry for a
rectangle part using the :meth:`waves.scons_extensions.abaqus_journal_builder_factory` builder from the
:class:`waves.scons_extensions.WAVESEnvironment` construction environment (click the builder's name to link to the
|PROJECT| :ref:`waves_scons_api` API).

6. Create an ``SConscript`` file with the non-default name ``tutorial_01_geometry`` using the contents below.

.. admonition:: waves-tutorials/tutorial_01_geometry

    .. literalinclude:: tutorials_tutorial_01_geometry
        :language: Python
        :lineno-match:
        :end-before: marker-1
        :emphasize-lines: 15

The ``SConscript`` file begins with imports of standard Python libraries. The first
highlighted line imports the ``env`` variable (``Import('env')``), which is a variable set
in ``waves-tutorials/SConstruct`` file. The ``env`` variable defines project settings,
and is imported so settings variables are not hard-coded more than once.

7. Continue editing the file ``tutorial_01_geometry`` using the contents below.

.. admonition:: waves-tutorials/tutorial_01_geometry

     .. literalinclude:: tutorials_tutorial_01_geometry
         :language: Python
         :lineno-match:
         :start-after: marker-1
         :end-before: marker-3

First, the ``workflow`` variable is assigned to an empty list. Eventually, ``workflow``
will become a list of targets to build. Every time we instruct SCons to build a target or targets,
we will ``extend`` this list and finally create an alias that matches the parent
directory name. The alias thus represents the list of targets specified in the
``SConscript`` file.

The final block of code instructs SCons on how to build the targets, an Abaqus CAE file and an Abaqus journal file. The
source file is specified as an absolute path using the SCons feature ``#`` which refers to the project root directory.
Using an absolute path allows us to run the journal file without copying it to the build directory. The SCons ``#``
feature allows us to construct an absolute path that is correct with respect to the current ``SConstruct`` file location
even if the project is moved or copied somewhere else on the filing system. ``subcommand_options`` allows for parameters to
be passed as command-line arguments to the journal file.  Using the journal file's command-line interface with the
``subcommand_options`` string will be discussed in :ref:`tutorial_parameter_substitution`.

Next, the ``workflow`` list is extended to include the action to use the :meth:`waves.scons_extensions.abaqus_journal_builder_factory` builder,
as discussed in :ref:`tutorialsconstruct`. For more information about the behavior of the
:meth:`waves.scons_extensions.abaqus_journal_builder_factory` builder, click the builder's link or see the |PROJECT| :ref:`waves_scons_api`
API. The ``target`` list specifies the files created by the :meth:`waves.scons_extensions.abaqus_journal_builder_factory` task's action, which
is defined in the :ref:`waves_scons_api` API.

8. Continue editing the file ``tutorial_01_geometry`` using the contents below.

.. admonition:: waves-tutorials/tutorial_01_geometry

     .. literalinclude:: tutorials_tutorial_01_geometry
         :language: Python
         :lineno-match:
         :start-after: marker-3

First, we create an alias for the workflow that was extended previously to match the name of the current file, which
will double as the build directory name: ``tutorial_01_geometry``.

The final lines of code in this ``SConscript`` file allow SCons to skip building a target
sequence if the Abaqus executable is not found.

*******************
Abaqus Journal File
*******************

Now that you have an overview of the ``SConscript`` file and how SCons uses an Abaqus journal
file, let's create the geometry part build file for the rectangle model.

The following sections of this tutorial will introduce four software-engineering practices
that match the build system philosophy. These concepts will be presented sequentially,
starting with familiar Abaqus Python code, and adding in the following:

* Protecting your code within a ``main()`` function
* Writing docstrings for your Python code
* Adding a command-line interface to your Python code
* Protecting ``main()`` function execution and returning exit codes

9. In the ``modsim_package/abaqus`` directory, create a file called ``rectangle_geometry.py``
   using the contents below which contains the ``main()`` function.

.. admonition:: waves-tutorials/modsim_package/abaqus/rectangle_geometry.py

    .. literalinclude:: abaqus_rectangle_geometry.py
        :language: Python
        :lineno-match:
        :end-before: marker-1
        :emphasize-lines: 11-23

It is important to note that ``rectangle_geometry.py`` is, indeed, an Abaqus journal
file - even though it does not look like a journal file produced by an Abaqus CAE GUI
session.

.. _tutorial_geometry_waves_main_functions:

``main`` Functions
==================

The top of the file imports standard library modules used by the script's functions along with Abaqus modules. The
``main()`` function takes in several arguments, like ``model_name``, ``part_name``, and some geometric parameters for
the rectangle part. Most notable of the inputs to the ``main()`` function is the first input argument -
``output_file``. One can simplify the general concept of a build system into a series of inputs (known as sources) and
outputs (known as targets). In this case, the ``output_file`` is the target which is created from the source - the
``rectangle_geometry.py`` file.

.. _tutorial_geometry_waves_python_docstrings:

Python Docstrings
=================

The highlighted lines of code at the beginning of the ``main()`` function are called a docstring.  Docstrings are
specially formatted comment blocks that help automate documentation builds. In this case, the docstrings are formatted so
the `Sphinx automodule`_ directive can interpret the comments as ReStructured Text. Docstrings discuss the function
behavior and its interface. See the `PEP-257`_ conventions for docstring formatting along with `PEP-287`_ for syntax
specific to reStructured Text. Using the `Sphinx automodule`_ directive, the docstring can be used to autobuild
documentation for your functions. An example of this is in the :ref:`waves_tutorial_api` for
:ref:`abaqus_rectangle_geometry_api`.

.. _tutorial_geometry_waves_abaqus_python_code:

Abaqus Python Code
==================

The latter portion of the ``main()`` function is the code that generates the rectangle geometry. Here, an Abaqus model
is opened using the ``model_name`` variable as the model's name, a rectangle is drawn with dimensions ``width`` and
``height``, and the Abaqus CAE model is saved with the name ``output_file``. One notable difference between the `Abaqus
Scripting`_ documentation :cite:`ABAQUS` of Abaqus journal files is the use of the `PEP-8`_ style guide for package
imports.  Here, we order the imports according to the `PEP-8`_ style and avoid bulk imports to the file's namespace from
Abaqus Python packages. It is also worth noting that Abaqus journal files use the Abaqus Python environment *not*
the SCons Python environment. See the `Abaqus Python Environment`_ documentation :cite:`ABAQUS` for more information
on the Abaqus Python environment, noting that prior to Abaqus 2024, Abaqus shipped with Python 2.7 instead of Python 3.
The tutorials in this project supply journal files compatible with both Python 2.7 and Python 3.

.. _tutorial_geometry_waves_command_line_interfaces:

Command-Line Interfaces
=======================
10. In the ``modsim_package/abaqus`` directory, continue editing the file called ``rectangle_geometry.py``
    using the contents below containing the ``get_parser()`` function. Note that missing line numbers may be ignored.

.. admonition:: waves-tutorial/modsim_package/abaqus/rectangle_geometry.py

    .. literalinclude:: abaqus_rectangle_geometry.py
        :language: Python
        :lineno-match:
        :start-after: marker-1
        :end-before: marker-2
        :emphasize-lines: 12-14, 16-23, 25-61

This portion of ``rectangle_geometry.py`` defines the argument parsing function, ``get_parser()``, which is the
next step in turning our simple Python script into a small software utility. Command-line interfaces allow for scripts
to be executed with optional command-line arguments. This allows us to change the values of input arguments to the
``main()`` function without any source code modification.  ``argparse`` also helps automate command-line interface (CLI)
documentation. An example of this is the :ref:`waves_tutorial_cli` for :ref:`abaqus_rectangle_geometry_cli`.
See the `Argparse tutorial`_ for an introduction to the ``argparse`` module.

The first highlighted portion of the ``get_parser()`` function defines variables based on the name of the script. While
this method of determining the file name is non-standard for Python 3, the Abaqus Python 2.7 environment necessitates
this syntax. This code will become common boilerplate code included in every Abaqus journal file created in the
tutorials. It is valuable to the behavior of these example journal files, but may not be required for all journal files
depending on their designed behavior.

The code that follows uses the name of the script to define some variables. This code
assumes that the ``part_name`` variable will be equal to the name of the script and will
remove the ``_geometry`` suffix if it exists in the file name.

The default values and naming conventions in this journal file are modsim project design decisions made for the
|PROJECT| tutorials and :ref:`modsim_templates`. In practice, it may be beneficial to choose different default behavior
depending on the design of the modsim project.

The second highlighted portion defines default values for some of the command-line arguments. Default values are
assigned if no command-line argument is detected for any of the expected command-line arguments. This provides sensible
defaults even when no command-line arguments are specified. It should be noted, however, that some model developers may
prefer to require all command-line arguments every time the file is used to build a target. ``output_file`` is the name
of the file that is created at the end of the ``main()`` function, which assumes ``output_file`` does not include a file
extension. ``default_width`` and ``default_height`` define the size of the ``rectangle`` part.

The final highlighted portion of the code is where the ``argparse`` package is used to
define the argument parser rules. First, an argument parser is defined using the
``ArgumentParser`` class. This receives a brief description ``cli_description`` and
direction ``prog`` on how to execute the program. Each subsequent call of the
``add_argument`` method adds a command-line argument to the parser's rules. Command-line
arguments defined using ``argparse`` have options, like ``-o`` or ``--output-file``, and
arguments. Arguments can also have default values. ``argparse`` also allows for command
line argument definitions to include a help message that is used to auto-generate the
command's help message. See the `Python argparse`_ documentation for more information.

In this case, we are using ``argparse`` in an Abaqus Python script, which will use Python
2.7. See the `Python 2.7 argparse`_ documentation for more information about how
``argparse`` will behave in an Abaqus journal file.

11. In the ``modsim_package/abaqus`` directory, continue editing the file called ``rectangle_geometry.py``
    using the contents below to create the ``if`` statement within which we will call the
    ``main()`` function. Note that missing line numbers may be ignored.

.. admonition:: waves-tutorials/modsim_package/abaqus/rectangle_geometry.py

    .. literalinclude:: abaqus_rectangle_geometry.py
        :language: Python
        :lineno-match:
        :start-after: marker-2

.. _tutorial_geometry_waves_top_level_code_environment:

Top-Level Code Environment
==========================
When the script is executed, an internal variable ``__name__`` is set to the value
``__main__``. When this condition is true (i.e. the script is being executed rather than
being imported), the code inside of ``main()`` is executed. ``__main__`` is referred to as
the top-level code environment. Top-level code is also referred to as the *entry point*
of the program. See the `Python Top-Level Code Environment`_ documentation for more
information.

The first lines within the ``if __name__ == "__main__"`` context call the
``get_parser()`` method and use ``argparse`` to separate known and unknown command-line
arguments. This is required for Abaqus journal files, because Abaqus will not strip the
CAE options from the ``abaqus cae -nogui`` command, which are irrelevant to and unused by
the journal file interface.

.. _tutorial_geometry_waves_retrieving_exit_codes:

Retrieving Exit Codes
=====================

The ``main()`` function is called from within the ``sys.exit()`` method. This provides
the operating system with a non-zero exit code if the script throws an error. By
convention, non-zero exit codes indicate an error in the executing program. See the `Bash
Exit Status`_ documentation for more information about specific exit codes. This is used
by build systems to understand when a target has not been produced correctly and to exit the
downstream sequence of target actions which can no longer succeed.

Entire Abaqus Journal File
==========================

Shown below is ``rectangle_geometry.py`` in its entirety. The highlighted lines show the non-boilerplate code that will
change between journal files in the tutorials. As discussed in preceding sections, some portions of the boilerplate code
are required for modsim project best practice when using a build system such as `SCons`_ and other sections are
boilerplate code that matches naming conventions used by the tutorials, but that may change in production modsim
projects.

.. admonition:: waves-tutorials/modsim_package/abaqus/rectangle_geometry.py

     .. literalinclude:: abaqus_rectangle_geometry.py
         :language: Python
         :linenos:
         :emphasize-lines: 11-23, 26-38, 62, 66-68, 71, 73-105, 126-130

***************
SConstruct File
***************

In :ref:`tutorialsconstruct`, we created the ``SConstruct`` file. For convenience, we will add a collector alias
matching the tutorial directory name in the SContruct file. This collector alias will point to the list of targets to
build specified in the ``waves-tutorials/tutorial_01_geometry`` file.

12. Modify the ``waves-tutorials/SConstruct`` file by adding the
    ``tutorial_01_geometry`` collector alias to the ``workflow_configurations`` list.
    The ``diff`` output below shows the difference between the ``SConstruct`` file created
    in :ref:`tutorialsconstruct` and what the new ``SConstruct`` file will be.

    .. admonition:: waves-tutorials/SConstruct diff

        .. literalinclude:: tutorials_tutorial_01_geometry_SConstruct
           :language: Python
           :diff: tutorials_tutorial_00_SConstruct

.. _tutorial_geometry_waves_build_targets:

****************
Building Targets
****************

Now that you've created the geometry task in ``tutorial_01_geometry``, this section will walk through building the
``tutorial_01_geometry`` targets using Scons.

13. To build the targets only for the ``tutorial_01_geometry`` workflow, execute the following
    command:

    .. code-block::

        $ pwd
        /home/roppenheimer/waves-tutorials
        $ scons tutorial_01_geometry
        scons: Reading SConscript files ...
        Checking whether /apps/abaqus/Commands/abq2024 program exists.../apps/abaqus/Commands/abq2024
        Checking whether abq2024 program exists.../apps/abaqus/Commands/abq2024
        scons: done reading SConscript files.
        scons: Building targets ...
        cd /home/roppenheimer/waves-tutorials/build/tutorial_01_geometry && /apps/abaqus/Commands/abq2024 cae -noGui
        /home/roppenheimer/waves-tutorials/modsim_package/abaqus/rectangle_geometry.py -- > rectangle_geometry.cae.stdout 2>&1
        scons: done building targets.

The default build directory name is ``build`` and located in the same parent directory as
the ``SConstruct`` file as described in :ref:`tutorialsconstruct`.

************
Output Files
************

Explore the contents of the ``build`` directory using the ``tree`` command against the ``build`` directory, as shown
below. Note that the directory structure of the build directory *exactly* matches the directory structure of the
location where the project-level ``SConstruct`` and ``SConscript`` files exist. This behavior will allow us to define
multiple simulations in our :term:`modsim repository` with build result separation if more than one simulation is built
at the same time. :ref:`tutorial_partition_mesh` will demonstrate the importance of this behavior more clearly.

.. code-block:: bash

   $ pwd
   /home/roppenheimer/waves-tutorials
   $ tree build/tutorial_01_geometry/
   build/tutorial_01_geometry/
   |-- abaqus.rpy
   |-- rectangle_geometry.cae
   |-- rectangle_geometry.cae.stdout
   `-- rectangle_geometry.jnl

   0 directories, 4 files

At this point, the only directory in the ``build`` directory is that pertaining to the
specific target that was specified to be built. In this case, that is
``tutorial_01_geometry``.

The ``build/tutorial_01_geometry/`` directory should contain the following files:

* ``abaqus.rpy``, the replay file from the ``abaqus cae -nogui`` command
* ``rectangle_geometry.cae``, an Abaqus CAE file that contains a model named
  ``model_name`` within which is a part named ``part_name``.
* ``rectangle_geometry.jnl`` and ``rectangle_geometry.cae.stdout``, the journal file
  that records all of the commands executed by Abaqaus and the log file that will contain
  any errors recorded by Abaqus.

**********************
Workflow Visualization
**********************

To visualize the workflow, you can use the |project| :ref:`waves_visualize_cli` command. The ``--output-file`` allows
you to save the visualization file non-interactively. Without this option, you'll enter an interactive matplotlib window.

.. code-block::

   $ pwd
   /home/roppenheimer/waves-tutorials
   $ waves visualize tutorial_01_geometry --output-file tutorial_01_geometry.png --width=16 --height=3
   $ ls tutorial_01_geometry.png
   tutorial_01_geometry.png

The workflow visualization should look similar to the image below, which is a representation of the directed graph
constructed by `SCons`_ from the task definitions. The image starts with the final workflow target on the left, in this
case the tutorial target alias. Moving left to right, the files required to complete the workflow are shown until we
reach the original source file(s) on the far right of the image. The arrows represent actions and are drawn from a
required source to the produced target. The :ref:`computational_tools` introduction discusses the relationship of a
:ref:`build_system` task and :ref:`build_system_directed_graphs`.

.. raw:: latex

    \begin{landscape}
        \vspace*{\fill}

.. figure:: tutorial_01_geometry.png
   :align: center
   :width: 100%

.. raw:: latex

        \vspace*{\fill}
    \end{landscape}

In this case, the single source file ``rectangle_geometry.py`` is producing several output files which are required by
the workflow. Notice that only two of these files were specified in our geometry task: ``rectangle_geometry.cae`` and
``rectangle_geometry.jnl``. The ``rectangle_geometry.cae.stdout`` files is generated as part of the ``AbaqusJournal``
builder and appended automatically during task generation. This workflow visualization will become crowded quickly in
these tutorials, so future visualization commands will show you how to ignore specific file extensions to reduce visual
clutter.

This workflow graph would be relatively easy to manage manually for this simple introductory tutorial. However, as the
core tutorials grow in file count, and especially when we start adding parameter studies, it will become more obvious
why a build system is desirable to manage modsim workflows.
