.. _tutorial01geometrywaves:

####################
Tutorial 1: Geometry
####################

**Do the following steps to get started with hands-on activities:**

1. Create two directories ``tutorial_01_geometry`` and and ``source`` with the same parent 
   directory. For example, in a bash shell:
   
   .. code-block:: bash
       
       $ pwd
       /path/to/local/clone/eabm
       $ mkdir tutorial_01_geometry source

2. Create a directory within ``source`` called ``abaqus``. For example, in a bash shell:

   .. code-block:: bash
   
       $ pwd
       /path/to/local/clone/eabm
       $ mkdir source/abaqus

       
***************
SConscript File
***************

.. admonition:: SConscript
   
    .. literalinclude:: tutorial_01_geometry_SConscript
        :language: Python
        :lineno-match:
        :end-before: marker-1

.. admonition:: Sconscript

     .. literalinclude:: tutorial_01_geometry_SConscript
         :language: Python
         :lineno-match:
         :start-after: marker-1


***********************************
Create geometry part build file
***********************************

Now that you have an overview of the SConscript file and how SCons uses an Abaqus journal 
file, let's create the geometry part build file for the single element model.

The following sections of this tutorial will introduce four software-engineering practices 
that are paramount to building an EABM. These concepts will be presented sequentially, 
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
file - even though it does not have the classic ``.jnl.py`` extension. By using a standard 
Python ``.py`` extension for the journal file, we allow the Sphinx Python interpreter to 
read the file as if it is true Python, and this allows for automated API generation from 
docstrings (which are disussed in the following paragraphs).

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
In this case, the docstrings are formatted so the Sphinx ``automodule`` directive can 
interpret the comments as ReStructured Text. Docstrings discuss the use case of the 
function along with its inputs, outputs, and usage.

Abaqus Python Code
==================

The latter portion of the ``main`` function is the code that generates the single element 
geometry. Here, an Abaqus model is opened using the ``model_name`` variable as the model's 
name, a rectangle is drawn with dimensions ``width`` and ``height``, and the Abaqus model 
is saved with the name ``<output_file>.cae``.

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

This portion of ``single_element_geometry.py`` defines the argument parsing function, 
:meth:`get_parser`, which is the next step in turning our simple Python script into a 
small software utility. Command line interfaces allow for scripts to be executed with 
changing input arguments to the ``main`` function without any source code modification.

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

Retrieving Exit Codes
=====================

The :meth:`main` function is called from within the :meth:`sys.exit` method. This provides 
the operating system with a non-zero exit code if the script throws and error.


****************
Building targets
****************

Now that you've create the geometry part build file in your ``tutorial_01_geometry`` 
folder, this section will walk through building the ``tutorial_01_geometry`` target using 
Scons.

.. todo::

    To build the targets only for the ``tutorial_01_geometry``, execute the following 
    command: ``scons tutorial_01_geometry``

    To build *all* targets aliases in the ``eabm/SConstruct`` file, execute the following 
    command: ``scons .``
    
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
    /path/to/local/clone/eabm
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
