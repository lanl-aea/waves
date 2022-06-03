.. _quickstart:

##########
Quickstart
##########

This quickstart will create a minimal, single file version of the full tutorial project definitions in

* :ref:`tutorialgeometrywaves`
* :ref:`tutorial_partition_mesh`
* :ref:`tutorial_solverprep`
* :ref:`tutorial_simulation`

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

5. Download and copy the following modsim files into the ``source/abaqus`` sub-directory.

***************
SConstruct File
***************

5. Create a file named ``SConstruct`` from the contents below.

.. admonition:: waves-eabm-tutorial/SConstruct
   
    .. literalinclude:: eabm_quickstart_SConstruct
       :language: Python
       :lineno-match:
