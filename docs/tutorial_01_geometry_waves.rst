.. _tutorialgeometrywaves:

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

Below is a list of refrences for more information about topics that are not explicitly 
covered in this tutorial.

* `Abaqus Scripting`_
* `Abaqus Python Environment`_
* Python Docstrings: `PEP-257`_, `PEP-287`_

***********
Environment
***********

.. include:: tutorial_environment_activation.txt

*******************
Directory Structure
*******************

3. Within the ``waves-eabm-tutorial`` directory, create two directories called 
   ``tutorial_01_geometry`` and ``source/abaqus``. For example, in a bash shell:
   
   .. code-block::
       
       $ pwd
       /path/to/waves-eabm-tutorial
       $ mkdir tutorial_01_geometry source/abaqus

***************
SConscript File
***************

The ``SConscript`` file defines the sources, actions, and targets. Sources are 
files that exist in the source repository, such as Abaqus journal files. Actions define 
how to process source files, for example executing the Abaqus command. Targets are the 
output artifacts created by the action, such as an Abaqus model file. It is also worth 
noting that the ``SConscript`` file naming convention is case sensitive.
In this tutorial, we will build the geometry for a single element part using the 
:meth:`waves.builders.abaqus_journal` builder (click the builder's name to link to the 
:ref:`waves_builders_api`).

4. In the ``tutorial_01_geometry`` directory, create a file called ``SConscript`` using 
the contents below.

.. admonition:: SConscript
   
    .. literalinclude:: tutorial_01_geometry_SConscript
        :language: Python
        :lineno-match:
        :end-before: marker-1
        :emphasize-lines: 6, 9-11

The ``SConscript`` file begins with imports of standard Python libraries. The first 
highlighted line imports the ``env`` variable (``Import('env')``), which is a variable set 
in ``waves-eabm-tutorial/SConstruct`` file. The ``env`` variable defines project settings, 
and is imported so settings variables are not hard-coded more than once.

The next set of highlighted lines sets operating system agnostic paths by utilizing 
`Python pathlib`_ objects. These Pathlib objects absolute or relative paths on any 
operating system to source files using variables defined in the 
``waves-eabm-tutorial/SConstruct`` file. This method of path definition allows for 
path-strings to be hard-coded only once, and then used as variables everywhere else in 
the code. For example, the variable ``abaqus_source_abspath`` is used in source 
definitions to point at the absolute path to the directory where the Abaqus journal files 
exist.

5. In the ``tutorial_01_geometry`` directory, continue editing the file called 
``SConscript`` using contents below.

.. admonition:: Sconscript

     .. literalinclude:: tutorial_01_geometry_SConscript
         :language: Python
         :lineno-match:
         :start-after: marker-1
         :end-before: marker-2
         :emphasize-lines: 5-10

First, the ``workflow`` variable is assigned to an empty list. Eventually, ``workflow`` 
will become a list of targets to build. Every time we instruct SCons to build a target(s), 
we will ``extend`` this list and finally create an alias that matches the parent 
directory name. The alias thus represents the list of targets specified in the 
``SConscript`` file.

The highlighted lines of code instruct SCons on how to build the target, an Abaqus CAE 
file whose name is constructed using the ``journal_file`` variable. The ``journal_file`` 
variable exists solely to minimize hard-coded duplication of the string 
``'single_element_geometry'``. ``journal_options`` allows for parameters to be passed as 
command line arguments to the journal file. Using the journal file's command line 
interface with the ``journal_options`` string will be discussed in 
REFTUTORIALK05PLACEHOLDER.

Next, the ``workflow`` list is extended to include the action to use the 
:meth:`waves.builders.abaqus_journal` builder, as discussed in :ref:`tutorialsconstruct`. 
For more information about the behavior of the 
:meth:`waves.builders.abaqus_journal` builder, click the builder's link or see the 
:ref:`waves_builders_api`. The ``target`` list specifies the files created by the 
:meth:`waves.builders.abaqus_journal` task's action, which is defined in the 
:ref:`waves_builders_api`.

6. In the ``tutorial_01_geometry`` directory, continue editing the file called 
``SConscript`` using the contents below.

.. admonition:: Sconscript

     .. literalinclude:: tutorial_01_geometry_SConscript
         :language: Python
         :lineno-match:
         :start-after: marker-2

First, we create an alias for the workflow that was extended previously to the name 
of the current working directory, in this case ``tutorial_01_geometry``.

The final lines of code in the ``SConstruct`` file allow SCons to skip building a target 
sequence if the Abaqus executable is not found.

*******************
Abaqus Journal File
*******************

Now that you have an overview of the ``SConscript`` file and how SCons uses an Abaqus journal 
file, let's create the geometry part build file for the single element model.

The following sections of this tutorial will introduce four software-engineering practices 
that match the build system philosophy. These concepts will be presented sequentially, 
starting with familiar Abaqus Python code, and adding in the following:

* Protecting your code within a ``main()`` function
* Writing docstrings for your Python code
* Adding a command line interface to your Python code
* Protecting ``main()`` function execution and returning exit codes

7. In the ``source/abaqus`` directory, create a file called ``single_element_geometry.py``
   using the contents below which contains the ``main()`` function.

.. admonition:: single_element_geometry.py
   
    .. literalinclude:: abaqus_single_element_geometry.py
        :language: Python
        :lineno-match:
        :end-before: marker-1
        :emphasize-lines: 10-21

It is important to note that ``single_element_geometry.py`` is, indeed, an Abaqus journal 
file - even though it does not look like a journal file produced by an Abaqus CAE GUI 
session.

``main`` Functions
==================
The top of the file imports standard library modules used by the script's functions along 
with Abaqus modules. The ``main()`` function takes in several arguments, like  
``model_name``, ``part_name``, and some geometric parameters for the single element 
part. Most notable of the inputs to the ``main()`` function is the first input argument - 
``output_file``. One can simplify the general concept of a build system into a series of 
inputs (known as sources) and outputs (known as targets). In this case, the 
``output_file`` is the target which is created from the source - the 
``single_element_geometry.py`` file.

Python Docstrings
=================
The highlighted lines of code at the beginning of the ``main()`` function are called a docstring. 
Docstrings are specially formatted comment blocks the help automate documentation builds. 
In this case, the docstrings are formatted so the `Sphinx automodule`_ directive can 
interpret the comments as ReStructured Text. Docstrings discuss the function behavior and 
its interface. See the `PEP-257`_ conventions for docstring formatting along with 
`PEP-287`_ for syntax specific to reStructured Text. Using the `Sphinx automodule`_ 
directive, the docstring can be used to autobuild documentation for your functions. An 
example of this is in the `EABM API`_.

Abaqus Python Code
==================
The latter portion of the ``main()`` function is the code that generates the single 
element geometry. Here, an Abaqus model is opened using the ``model_name`` variable as 
the model's name, a rectangle is drawn with dimensions ``width`` and ``height``, and the 
Abaqus CAE model is saved with the name ``output_file``. One notable difference between 
the `Abaqus Scripting`_ documentation of Abaqus journal files is the use of the 
`PEP-8`_ style guide for package imports. Here, we order the imports according to the 
`PEP-8`_ style and avoid bulk imports to the file's namespace from Abaqus Python 
packages. It is also worth noting noting that Abaqus journal files use the the Abaqus 
Python 2.7 environment *not* the SCons/EABM Python 3 environment. See the 
`Abaqus Python Environment`_ documentation for more information on the 
Abaqus Python 2.7 environment.

.. TODO link to abaqus scripting documentation, specifically mention python 2.7

Command Line Interfaces
=======================
8. In the ``source/abaqus`` directory, continue editing the file called ``single_element_geometry.py``
   using the contents below which contains the ``get_parser()`` function. Note that 
   missing line numbers may be ignored.

.. admonition:: single_element_geometry.py

    .. literalinclude:: abaqus_single_element_geometry.py
        :language: Python
        :lineno-match:
        :start-after: marker-1
        :end-before: marker-2
        :emphasize-lines: 3-5, 12-14, 16-30

This portion of ``single_element_geometry.py`` defines the argument parsing function, 
``get_parser()``, which is the next step in turning our simple Python script into a 
small software utility. Command line interfaces allow for scripts to be executed 
with optional command line arguments. This allows us to change the values of input 
arguments to the ``main()`` function without any source code modification. 
``argparse`` also helps automate command line interface (CLI) documentation. An example of 
this is the `EABM CLI`_.

The first highlighted portion of the ``get_parser()`` function defines variables based on 
the name of the script. While this method of determining the file name is non-standard 
for Python 3, the Abaqus Python environment neccessitates this syntax. This code will 
become common boilerplate code included in every Abaqus journal file created in the 
WAVES-EABM tutorials. It is valuable to the behavior of these example journal files, but 
may not be required for all journal files depending on their designed behavior.

The code that follows uses the name of the script to define some variables. This code 
assumes that the ``part_name`` variable will be equal to the name of the script and will 
remove the ``_geometry`` suffix if it exists in the file name.

The default values and naming conventions in this journal file are eabm design decisions 
made for this EABM stub repository. In practice, it may be beneficial to choose different 
default behavior depending on the design of the EABM.

The second highlighted portion defines default values for some of the command 
line arguments. Default values are assigned if no command line argument is detected for any of 
the expected command line arguments. This provides the utility of having a use-able file 
even when command line arguments are not specified. It should be noted, however, that 
some model developers may prefer to require all command line arguments every time the 
file is used to build a target. ``output_file`` is the name of the file that is created 
at the end of the ``main()`` function, which assumes ``output_file`` does not include a 
file extension. ``default_width`` and ``default_height`` define the size of the 
``single_element`` part.

The final highlighted portion of the code is where the ``argparse`` package is used to 
define the argument parser rules. First, an argument parser is defined using the 
``ArgumentParser`` class. This recieves a brief description ``cli_description`` and 
direction ``prog`` on how to execute the program. Each subsequent call of the 
``add_argument`` method adds a command line argument to the parser's rules. Command line 
arguments defined using ``argparse`` have options, like ``-o`` or ``--output-file``, and 
arguments. Arguments can also have default values. ``argparse`` also allows for command 
line argument definitions to include a help message that is used to auto-generate the 
command's help message. See the `Python argparse`_ documentation for more information.

In this case, we are using ``argparse`` in an Abaqus Python script, which will use Python 
2.7. See the `Python 2.7 argparse`_ documentation for more information about how 
``argparse`` will behave in an Abaqus journal file.

9. In the ``source/abaqus`` directory, continue editing the file called ``single_element_geometry.py``
   using the contents below to create the ``if`` statement within which we will call the 
   ``main()`` function. Note that missing line numbers may be ignored.

.. admonition:: single_element_geometry.py

    .. literalinclude:: abaqus_single_element_geometry.py
        :language: Python
        :lineno-match:
        :start-after: marker-2

Top-Level Code Environment
==========================
When the script is executed, an internal variable ``__name__`` is set to the value 
``__main__``. When this condition is true (i.e. the script is being executed rather than 
being imported), the code inside of ``main()`` is executed. ``__main__`` is referred to as 
the top-level code environment. Top-level code is also referred to as the *entry point* 
of the program. See the `Python Top-Level Code Environment`_ documentation for more 
information.

The first lines within the ``if __name__ == "__main__"`` context call the 
``get_parser()`` method and use ``argparse`` to separate known and unknown command line 
arguments. This is required for Abaqus journal files, because Abaqus will not strip the 
CAE options from the ``abaqus cae -nogui`` command, which are irrelevant to and unused by 
the journal file interface.

Retrieving Exit Codes
=====================
The ``main()`` function is called from within the ``sys.exit()`` method. This provides 
the operating system with a non-zero exit code if the script throws an error. By 
convention, non-zero exit codes indicate an error in the executing program. See the `Bash 
Exit Status`_ documentation for more infomation about specific exit codes. This is used 
by build systems to understand when a target has not been produced correctly and to exit the 
downstream sequence of target actions which can no longer succeed.

Entire Abaqus Journal File
==========================
Shown below is ``single_element_geometry.py`` in its entirety. The highlighted lines show 
the non-boilerplate code that will change between journal files in this WAVES-EABM 
tutorial project. As discussed in preceding sections, some portions of the boilerplate 
code are required for EABM best practice when using a build system such as SCons_ and 
other sections are boilerplate code that matches naming conventions used by the tutorials, 
but that may change in production EABMs.

.. admonition:: single_element_geometry.py

     .. literalinclude:: abaqus_single_element_geometry.py
         :language: Python
         :linenos:
         :emphasize-lines: 9-21, 25-36, 52, 55-58, 61, 64-74, 83-87

***************
SConstruct File
***************

In :ref:`tutorialsconstruct`, we created the ``SConstruct`` file. For convenicne, we will add a 
collector alias matching the tutorial direcotyr name in the SContruct file. This 
collector alias will point to the list of targets to build specified in the 
``waves-eabm-tutorial/tutorial_01_geometry/SConscript`` file.

10. Modify the ``waves-eabm-tutorial/SConstruct file`` by adding the 
    ``tutorial_01_geometry`` collector alias to the ``eabm_simulation_directories`` list.
    The ``diff`` output below shows the difference between the ``SConstruct`` file created 
    in :ref:`tutorialsconstruct` and what the new ``SConstruct`` file will be.
 
    .. admonition:: waves-eabm-tutorial/SConstruct diff
       
        .. literalinclude:: eabm_tutorial_01_geometry_SConstruct
           :language: Python
           :diff: eabm_tutorial_00_SConstruct

****************
Building targets
****************

Now that you've created the geometry part build file in your ``tutorial_01_geometry`` 
directory, this section will walk through building the ``tutorial_01_geometry`` targets 
using Scons.

11. To build the targets only for the ``tutorial_01_geometry``, execute the following 
    command: 

    .. code-block::
       
        $ pwd
        /path/to/waves-eabm-tutorial
        $ scons tutorial_01_geometry
        scons: Reading SConscript files ...
        Checking whether sphinx-build program 
        exists.../projects/aea_compute/aea-beta/bin/sphinx-build
        Checking whether abaqus program exists.../apps/abaqus/Commands/abaqus
        Checking whether cubit program exists.../apps/Cubit-15.8/cubit
        Checking whether abaqus_wrapper program exists...no
        Could not find 'abaqus_wrapper' in construction environment. Using WAVES internal 
        path.../projects/roppenheimer/waves/waves/bin/abaqus_wrapper
        scons: done reading SConscript files.
        scons: Building targets ...
        cd /projects/roppenheimer/waves/eabm/build/tutorial_01_geometry && 
        /apps/abaqus/Commands/abaqus -information environment > 
        single_element_geometry.abaqus_v6.env
        cd /projects/roppenheimer/waves/eabm/build/tutorial_01_geometry && 
        /apps/abaqus/Commands/abaqus cae -noGui 
        /projects/roppenheimer/waves/eabm/source/abaqus/single_element_geometry.py -- > 
        single_element_geometry.log 2>&1
        scons: done building targets.

The default build directory name is ``build`` and located in the same parent directory as 
the ``SConstruct`` file as described in :ref:`tutorialsconstruct`.    

************
Output Files
************

Explore the contents of the ``build`` directory using the ``tree`` command against the 
``build`` directory, as shown below. Note that the directory structure of the build 
directory *exactly* matches the directory structure of the location where the 
project-level ``SConstruct`` and ``SConscript`` files exist. This behavior will allow us 
to define multiple simulations in our modsim repository (EABM) with build result 
separation if more than one simulation is built at the same time. 
:ref:`tutorialpartitionmeshwaves` will demonstrate the importance of this behavior more clearly.

.. code-block:: bash
    
    $ pwd
    /path/to/waves-eabm-tutorial
    $ tree build
    build/
    └── tutorial_01_geometry
        ├── abaqus.rpy        
        ├── single_element_geometry.abaqus_v6.env
        ├── single_element_geometry.cae
        ├── single_element_geometry.jnl
        └── single_element_geometry.log

    1 directory, 5 files

Inside the build directory are two sub-directories. First is a default ``docs`` directory 
that is specified to be built in the ``waves-eabm-tutorial/SConstruct`` file. Second is 
the directory pertaining to the specific target that was specified to be built. In this 
case, that is ``tutorial_01_geometry``. 

The ``tutorial_01_geomtry/`` directory should contain the following files:

* ``abaqus.rpy``, the replay file from the ``abaqus cae -nogui`` command
* ``single_element_geometry.abaqus_v6.env``, the environment file that allows for 
  reproduction of the Abaqus environment used to build the ``tutorial_01_geometry`` targets
* ``single_element_geomtry.cae``, an Abaqus CAE file that contains a model named 
  ``model_name`` within which is a part named ``part_name``.
* ``single_element_geometry.jnl`` and ``single_element_geometry.log``, the journal file 
  that records all of the commands executed by Abaqaus and the log file that will contain 
  any errors recorded by Abaqus.
