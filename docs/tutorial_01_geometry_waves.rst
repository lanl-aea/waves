.. _tutorialgeometrywaves:

#####################
Tutorial 01: Geometry
#####################

**********
References
**********


*******************
Directory Structure
*******************

1. Within the ``waves-eabm-tutorial`` directory, two directories called ``tutorial_01_geometry`` and and ``source``. 
   For example, in a bash shell:
   
   .. code-block::
       
       $ pwd
       /path/to/waves-eabm-tutorial
       $ mkdir tutorial_01_geometry source

2. Create a directory within ``source`` called ``abaqus``. For example, in a bash shell:

   .. code-block::
   
       $ pwd
       /path/to/waves-eabm-tutorial
       $ mkdir source/abaqus

       
***************
SConscript File
***************

The SConscript file defines the sources, actions, and targets. Sources are 
files that exist in the source repository, such as Abaqus journal files. Actions define 
how to process source files, for example executing the Abaqus command. Targets are the 
output artifacts created by the action, such as an Abaqus model file.
In this tutorial, we will build the geometry for a single element part using the 
:meth:`waves.builders.abaqus_journal` builder (click the builder's name to link to the 
:ref:`wavesbuildersapi`).

3. In the ``tutorial_01_geometry`` folder, create a file called ``SConscript``. Use the 
   contents below to create the first third of the file.

.. admonition:: SConscript
   
    .. literalinclude:: tutorial_01_geometry_SConscript
        :language: Python
        :lineno-match:
        :end-before: marker-1
        :emphasize-lines: 6, 9-11

The SConscript file begins with imports of standard Python libraries. The first 
highlighted line imports the ``env`` variable (``Import('env')``), which is a variable set 
in ``waves-eabm-tutorial/SConstruct`` file. The ``env`` variable defines project settings, 
and is imported so settings variables are not hard-coded more than once.

The next set of highlighted lines sets operating system agnostic paths by utilizing 
`Python pathlib`_ objects. Pathlib objects are used to reconstruct absolute paths to 
source files using variables defined in the ``waves-eabm-tutorial/SConstruct`` 
file. This method of path definition allows for path-strings to be hard-coded only once, 
and then used as variables everywhere else in the code. For example, the variable 
``abaqus_source_abspath`` is used in source definitions to point at the absolute path to 
the directory where the Abaqus journal files exist.

4. In the ``tutorial_01_geometry`` folder, modify the file called ``SConscript``. Use the 
   contents below to create the middle portion of the file

.. admonition:: Sconscript

     .. literalinclude:: tutorial_01_geometry_SConscript
         :language: Python
         :lineno-match:
         :start-after: marker-1
         :end-before: marker-2
         :emphasize-lines: 5-10

First, the ``workflow`` variable is assigned to an empty list. Every time we instruct 
SCons to build a target(s), we will ``extend`` this list and finally create an alias to the current
directory name for the workflow list of targets.

The highlighted lines of code (starting with ``journal_file = f"{model}_geometry"``) instruct 
SCons on how to build the ``journal_file`` target, which is an Abaqus CAE file. The 
``journal_file`` variable helps to construct the name of the source to perform the action 
on along with the name of the target that will be created. ``journal_options`` allows for 
parameters to be passed as command line arguments to the journal file. This will be 
discussed in REFTUTORIAL05PLACEHOLDER.

Next, the ``workflow`` list is extended to include the action to use the 
:meth:`waves.builders.abaqus_journal` builder, as discussed in REFTUTORIAL0PLACEHOLDER. 
For more information about the behavior of the 
:meth:`waves.builders.abaqus_journal` builder, click the builder's link or see the 
:ref:`wavesbuildersapi`. ``target`` specifies the files created when running the 
``source`` files with the Abaqus command.

5. In the ``tutorial_01_geometry`` folder, modify the file called ``SConscript``. Use the 
   contents below to create the final third of the file

.. admonition:: Sconscript

     .. literalinclude:: tutorial_01_geometry_SConscript
         :language: Python
         :lineno-match:
         :start-after: marker-2

First, we create an alias for the workflow that was extended previously to the name 
of the current working directory, in this case ``tutorial_01_geometry``.

The final lines of code in the ``SConstruct`` file allow SCons to skip building a target 
sequence if the Abaqus executable is not found.

Entire SConscript File
======================

Shown below is the SConscript file in its entirety. The highlighted lines indicate code 
that will commonly be change on a project-by-project basis.

.. admonition:: Sconscript

     .. literalinclude:: tutorial_01_geometry_SConscript
         :language: Python
         :lines: 1-14, 17-28, 30-36
         :linenos:
         :emphasize-lines: 14, 20-21


*******************
Abaqus Journal File
*******************

Now that you have an overview of the SConscript file and how SCons uses an Abaqus journal 
file, let's create the geometry part build file for the single element model.

The following sections of this tutorial will introduce four software-engineering practices 
that match the build system philosophy. These concepts will be presented sequentially, 
starting with familiar Python code, and adding in the following:

1. Protecting your code within a ``main()`` function
2. Writing docstrings for your Python code
3. Adding a command line interface to your Python code
4. Protecting ``main()`` function execution and returning exit codes

6. In the ``source/abaqus`` folder, create a file called ``single_element_geometry.py``. 
   Use the contents below to create the first half of the file, which contains the 
   ``main()`` function.

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
with Abaqus modules. The ``main`` function takes in several arguments, like  
``model_name``, ``part_name``, and some geometric parameters for the single element 
part. Most notable of the inputs to the ``main`` function is the first input argument - 
``output_file``. One can simplify the general concept of a build system into a series of 
inputs (known as sources) and outputs (known as targets). In this case, the 
``output_file`` is the target which is created from the source - the 
``single_element_geometry.py`` file.

Python Docstrings
=================

The highlighted lines of code at the beginning of the ``main`` function are called a docstring. 
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
Abaqus CAE model is saved with the name ``output_file``.

.. TODO link to abaqus scripting documentation, specifically mention python 2.7

Command Line Interfaces
=======================

7. In the ``source/abaqus`` folder, modify the file called ``single_element_geometry.py``. 
   Use the contents below to create the ``get_parser()`` function. Note that any missing 
   line numbers should be interpreted as blank lines.

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
arguments to the ``main`` function without any source code modification. 
``argparse`` also helps automate command line interface (CLI) documentation. An example of 
this is the `EABM CLI`_.

The first highlighted portion of the ``get_parser()`` function (starting with 
``filename = inspect.getfile(lambda: None)``) defines variables based on the name of the 
script. While this method of determining the file name is non-standard for Python 3, the 
Abaqus-Python environment neccessitates this syntax. Nonetheless, the code is general for 
any script name.

The code that follows uses the name of the script to define some variables. This code 
assumes that the ``part_name`` variable will be equal to the name of the script and will 
remove the ``_geometry`` suffix if it exists in the file name.

The second highlighted portion (starting with ``default_output_file = 
'{}'.format(basename_without_extension)``) defines default values for some of the command 
line arguments. Default values are assigned if no command line argument is detected for any of 
the expected command line arguments. ``output_file`` is the name of the file that is 
created at the end of the ``main()`` function, which assumes ``output_file`` does not 
include a file extension. ``default_width`` and ``default_height`` define the size of the 
``single_element`` part.

The final highlighted portion of the code (starting with ``prog = "abaqus cae -noGui {} 
--".format(basename)``) is where the ``argparse`` package is used to define the argument 
parser rules. First, an argument parser is defined using the ``ArgumentParser`` method. 
This recieves a brief description ``cli_description`` and direction ``prog`` on how to 
execute the program. Each subsequent call of the ``add_argument`` method adds a command 
line argument to the parser's rules. Command line arguments have identifiers, like ``-o`` 
or ``--output-file``, default values, and help messages.

See the `Python argparse`_ documentation for more information.

8. In the ``source/abaqus`` folder, modify the file called ``single_element_geometry.py``. 
   Use the contents below to create the ``if`` statement within which we will call the 
   ``main()`` function. Note that any missing line numberts should be interpreted as blank 
   lines.

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
CAE options from the ``abaqus cae -nogui`` command.

Retrieving Exit Codes
=====================

The ``main()`` function is called from within the ``sys.exit()`` method. This provides 
the operating system with a non-zero exit code if the script throws and error. Retrieving 
non-zero exit codes allows the build system to exit when a build action has failed and a 
target has not been produced corrrectly .

Entire Abaqus Journal File
==========================

Shown below is ``single_element_geometry.py`` in its entirety. The highlighted lines 
indicate code that will commonly be change on a project-by-project basis.

.. admonition:: single_element_geometry.py

     .. literalinclude:: abaqus_single_element_geometry.py
         :language: Python
         :lines: 1-40, 42-74, 76-85
         :linenos:
         :emphasize-lines: 9-21, 25-36, 50, 53-56, 59, 62-72, 79-83


****************
Building targets
****************

Now that you've create the geometry part build file in your ``tutorial_01_geometry`` 
folder, this section will walk through building the ``tutorial_01_geometry`` targets using 
Scons.

First, recall that we aliased the action for building the targets in the 
``waves-ebam-tutorial/tutorial_01_geometry/SConscript`` file to the name of the tutorial 
directory. In order for that alias to be available for specifing which targets to build 
(as was just done in the code block above), the name ``tutorial_01_geometry`` needed to 
be added to the ``waves-eabm-tutorial/SConstruct`` file. This was done in 
REFTUTORIAL0PLACEHOLDER, as shown in the included section of code below.

.. admonition:: SConstruct

    .. literalinclude:: eabm_SConstruct
        :language: Python
        :lines: 86-99
        :lineno-match:
        :emphasize-lines: 4

9. To build the targets only for the ``tutorial_01_geometry``, execute the following command: 

   .. code-block::
       
       $pwd
       /path/to/waves-eabm-tutorial
       $scons tutorial_01_geometry
       scons: Reading SConscript files 
       <output truncated>
       ...scons: done building targets.
    
The output files will be located in the ``build`` directory within the ``eabm`` folder. 
The location of the ``build`` directory is controlled in the ``waves-eabm-tutorial/SConstruct`` 
file.


************
Output Files
************

Query the contents of the ``build`` directory using the ``tree`` command against the 
``build`` directory, as shown below. Note that the directory structure of the build 
directory *exactly* matches the directory structure of the location where the 
project-level ``SConstruct`` and ``SConscript`` files exist.

.. code-block:: bash
    
    $ pwd
    /path/to/waves-eabm-tutorial
    $ tree build
    build/
    ├── docs
    │   └── SConscript
    └── tutorial_01_geometry
        ├── abaqus.rpy        
        ├── single_element_geometry.abaqus_v6.env
        ├── single_element_geometry.cae
        ├── single_element_geometry.jnl
        └── single_element_geometry.log

    2 directories, 6 files

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
