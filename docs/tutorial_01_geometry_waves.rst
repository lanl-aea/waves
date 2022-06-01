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

The SConscript defines the sources, actions, and targets. Sources are 
files that exist in the source repository, such as Abaqus journal files. Actions define 
how to process source files, for example executing the Abaqus command. Targets are the 
outputs artifacts created by the action, such as an Abaqus model file.
In this tutorial, we will build the geometry for a single element part using the WAVES 
``AbaqusJournal`` builder.

.. todo::

    * In the ``tutorial_01_geometry`` folder, create a file called ``SConscript``
    * Use the contents below to create the first half of the file

.. admonition:: SConscript
   
    .. literalinclude:: tutorial_01_geometry_SConscript
        :language: Python
        :lineno-match:
        :end-before: marker-1
        :emphasize-lines: 6, 8-10

The SConscript file begins with imports of standard Python libraries. The first highlighed 
section is an SCons specific requirement. By default, SCons does not build in the user's 
current environment. This ensures reproducability between users and environments. However, 
in this case we want to inherit the user's compute environment, so we must import ``env``, 
which is a variable set in EABM's SConstruct file.

The next set of highlighted lines sets environment agnostic paths by utilizing 
`Python pathlib`_ objects. The variable ``abaqus_source_abspath`` is used in source definitions
to point at the absolute path to the directory where the Abaqus journal files exist.

Lastly, the ``model`` variable is assinged so it can be used to specify an Abaqus journal file 
by name.

.. todo::

    * In the ``tutorial_01_geometry`` folder, modify the file called ``SConscript``
    * Use the contents below to create the second half of the file

.. admonition:: Sconscript

     .. literalinclude:: tutorial_01_geometry_SConscript
         :language: Python
         :lineno-match:
         :start-after: marker-1
         :emphasize-lines: 5-10

First, the ``workflow`` variable is assigned to an empty list. Every time we instruct 
SCons to build a target(s), we will ``extend`` this list and finally create an alias to the current
directory name to the workflow list of targets.

The next lines of code instruct SCons on how to build the ``<journal_file>.cae`` target.
The ``journal_file`` variable sets the name of the Abaqus journal file that should be ran. 
``journal_options`` allows for parameters to be passed as command line arguments to the 
journal file. This will be discussed in REFTUTORIAL05PLACEHOLDER.

Next, the ``workflow`` list is extended to include the action to use the ``AbaqusJournal`` 
builder. For more information about the behavior of the ``AbaqusJournal`` builder, see the 
:ref:`sconsbuildersapi`. ``target`` specifies the files created when running the 
``source`` files with the Abaqus command.

The lines of code that follow alias the workflow that was extended previously to the name 
of the current working directory, in this case ``tutorial_01_geometry``.

The final lines of code in the ``SConstruct`` file allow SCons to skip building a target 
sequence if the Abaqus executable is not found.

*******************
Abaqus Journal File
*******************

Now that you have an overview of the SConscript file and how SCons uses an Abaqus journal 
file, let's create the geometry part build file for the single element model.

The following sections of this tutorial will introduce four software-engineering practices 
that match the build system philosophy. These concepts will be presented sequentially, 
starting with familiar Python code, and adding in the following:

1. Protecting your code within a :meth:`main` function
2. Writing docstrings for your Python code
3. Adding a command line interface to your Python code
4. Protecting :meth:`main` function execution and returning exit codes


.. todo::

    * In the ``abaqus`` folder, create a file called ``single_element_geometry.py``.
    * Use the contents below to create the first half of the file, which contains the 
      ``main`` function.

.. admonition:: single_element_geometry.py
   
    .. literalinclude:: abaqus_single_element_geometry.py
        :language: Python
        :lineno-match:
        :end-before: marker-1
        :emphasize-lines: 10-21

It is important to note that ``single_element_geometry.py`` is, indeed, an Abaqus journal 
file - even though it does not look like a journal file produced by an ABaqus CAE gui 
sessions.

``main`` Functions
==================

The top of the file imports standard library modules used by the script's functions along 
with Abaqus modules. The ``main`` function takes in several arguments, like a 
``model_name``, ``part_name``, and some geometric parameters for the single element. Most 
notable of the inputs to the ``main`` function is the first input argument - 
``output_file``. One can simplify the general concept of a build system into a series of 
inputs, known as sources, and outputs, known as targets. In this case, the ``output_file`` 
is the target which is created from the source, which is the 
``single_element_geometry.py`` file.


Python Docstrings
=================

The highlighted lines of code at the beginning of the ``main`` function are called a docstring. 
Docstrings are specially formatted comment blocks the help automate documentation builds. 
In this case, the docstrings are formatted so the `Sphinx`_ ``automodule`` directive 
can 
interpret the comments as ReStructured Text. Docstrings discuss the function behavior and 
its interface. See the `PEP-257`_ conventions for 
docstring formatting along with `PEP-287`_ for syntax specific to reStructured Text. Using 
the Sphinx ``automodule`` directive, the docstring can be used to autobuild documentation 
for your functions. An example of this is in the `EABM API`_.

Abaqus Python Code
==================

The latter portion of the ``main`` function is the code that generates the single element 
geometry. Here, an Abaqus model is opened using the ``model_name`` variable as the model's 
name, a rectangle is drawn with dimensions ``width`` and ``height``, and the Abaqus model 
is saved with the name ``<output_file>.cae``.

.. TODO link to abaqus scripting documentation, specifically mention python 2.7

Command Line Interfaces
=======================

.. todo::

    * In the ``abaqus`` folder, modify the file called ``single_element_geometry.py``.
    * Use the contents below to create the :meth:`get_parser` function. Note that any missing 
      line numbers should be interpreted as blank lines.

.. admonition:: single_element_geometry.py

    .. literalinclude:: abaqus_single_element_geometry.py
        :language: Python
        :lineno-match:
        :start-after: marker-1
        :end-before: marker-2
        :emphasize-lines: 2-5, 12-14, 16-30

This portion of ``single_element_geometry.py`` defines the argument parsing function, 
:meth:`get_parser`, which is the next step in turning our simple Python script into a 
small software utility. Command line interfaces allow for scripts to be executed with 
changing input arguments to the ``main`` function without any source code modification. 
``argparse`` also helps automate command line interface (CLI) documentation. An example of 
this is the `EABM CLI`_.

The first highlighted portion o the :meth:`get_parser` function defines variables based on 
the name of the script. While this method of determining the file name is non-standard for 
Python 3, the Abaqus-Python environment neccessitates this syntax. Nonetheless, the code 
is general for any script name.

The code that follows uses the name of the script to define some variables. This code 
assumes that the ``part_name`` variable will be equal to the name of the script, will 
remove the ``_geometry`` suffix if it exists in the file name.

The second highlighted portion defines default values for some of the command line 
arguments. Default values are assigned if no command line argument is detected for any of 
the expected command line arguments. ``output_file`` is the name of the file that is 
created at the end of the :meth:`main` function, which assumes ``output_file`` does not 
include a file extension. ``default_width`` and ``default_height`` define the size of the 
``single_element`` part.

The final highlighted portion of the code is where the ``argparse`` package is used to 
define the argument parser rules. First, an argument parser is defined using the 
:meth:`ArgumentParser` method. This recieves a brief description ``cli_description`` and 
direction ``prog`` on how to execute the program. Each subsequent call of the 
:meth:`add_argument` adds a command line argument to the parser's rules. Command line 
arguments have identifiers, like ``-o`` or ``--output-file``, default values, and help 
messages.

See the `Python argparse`_ documentation for more information.

.. todo::

    * In the ``source/abaqus`` folder, modify the file called ``single_element_geometry.py``.
    * Use the contents below to create the ``if`` statement within which we will call the 
      :meth:`main` function. Note that any missing line numberts should be interpreted as 
      blank lines.

.. admonition:: single_element_geometry.py

    .. literalinclude:: abaqus_single_element_geometry.py
        :language: Python
        :lineno-match:
        :start-after: marker-2

Top-Level Code Environment
==========================

When the script is executed, an internal variable ``__name__`` is set to the value 
``__main__``. When this condition is true (i.e. the script is being executed rather than 
being imported), the ``if`` statement's conditions are met, and the code inside is 
executed. ``__main__`` is referred to as the top-level code environment. Top-level code is 
also referred to as the *entry point* of the program. See the 
`Python Top-Level Code Environment`_ documentation for more information.

The first lines within the ``if __name__ == "__main__"`` context call the 
:meth:`get_parser` method and use ``argparse`` to separate known and unknown command line 
arguments. This is required for Abaqus journal files, because Abaqus will not strip the 
CAE options from the ``abaqus cae -nogui`` command.

Retrieving Exit Codes
=====================

The :meth:`main` function is called from within the :meth:`sys.exit` method. This provides 
the operating system with a non-zero exit code if the script throws and error.

allows the build system to exit when a build action has failed and a target has not been 
produced corrrectly 


****************
Building targets
****************

Now that you've create the geometry part build file in your ``tutorial_01_geometry`` 
folder, this section will walk through building the ``tutorial_01_geometry`` target using 
Scons.

.. todo::

    To build the targets only for the ``tutorial_01_geometry``, execute the following 
    command: ``scons tutorial_01_geometry``.

    reference back to sconstruct where default target list is 
    
    The output files will be located in the ``build`` directory within the ``eabm`` 
    folder. The location of the ``build`` directory is controlled in the 
    ``eabm/SConstruct`` file.


************
Output Files
************

Query the contents of the ``build`` directory using the ``tree`` command against the 
``build`` directory, as shown below.

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

    2 directories, 5 files

Inside the build directory are two sub-directories. First is a default ``docs`` directory 
that is specified to be built in the ``SConstruct`` file in the ``eabm`` root directory. 
Second is the directory pertaining to the specific target that was specified to be build. 
In this case, that is ``tutorial_01_geometry``. 

The ``tutorial_01_geomtry/`` directory should contain the following files:

* ``abaqus.rpy``, the replay file from the ``abaqus cae -nogui`` command
* ``single_element_geometry.abaqus_v6.env``, the environment file that allows for 
  reproduction of the Abaqus environment used to build the ``tutorial_01_geometry`` targets
* ``single_element_geomtry.cae``, an Abaqus CAE file that contains a model named 
  ``<model_name>`` within which is a part named ``<part_name>``.
* ``single_element_geometry.jnl`` and ``single_element_geometry.log``, the journal file 
  that records all of the commands executed by Abaqaus and the log file that will contain 
  any errors recorded by Abaqus.
