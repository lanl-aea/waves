.. _quickstart:

##########
Quickstart
##########

This quickstart will create a minimal version of the full tutorial project definitions below using a single project
definition file.

* :ref:`tutorialsconstruct`
* :ref:`tutorialgeometrywaves`
* :ref:`tutorial_partition_mesh_waves`
* :ref:`tutorial_solverprep_waves`
* :ref:`tutorial_simulation_waves`

***********
Environment
***********

.. include:: tutorial_environment_activation.txt

*******************
Directory Structure
*******************

3. Create the project directory structure and change to the project root directory with the following commands.

.. code-block:: bash

   $ pwd
   /home/roppenheimer
   $ mkdir -p waves-eabm-tutorial/source/abaqus
   $ cd /home/roppenheimer/waves-eabm-tutorial
   $ pwd
   /home/roppenheimer/waves-eabm-tutorial

4. Download and copy the `WAVES-EABM abaqus source files`_ into the ``source/abaqus`` sub-directory. If you're on a
   linux system with `git`_ installed and read access on the `WAVES`_ repository, you can use `git archive`_ as below.

.. code-block:: bash

   $ pwd
   /home/roppenheimer/waves-eabm-tutorial
   $ git archive --format=zip --remote=ssh://git@re-git.lanl.gov:10022/kbrindley/waves.git HEAD:eabm/source/abaqus > source_abaqus.zip
   $ unzip source_abaqus.zip -d source/abaqus


***************
SConstruct File
***************

5. Create a file named ``SConstruct`` from the contents below.

.. admonition:: waves-eabm-tutorial/SConstruct

    .. literalinclude:: eabm_quickstart_SConstruct
       :language: Python
       :lineno-match:

****************
Building targets
****************

.. code-block::
   
    $ pwd
    /path/to/waves-eabm-tutorial
    $ scons single_element
