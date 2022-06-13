.. _tutorial_simulation_waves:

#######################
Tutorial 04: Simulation
#######################

**********
References
**********

***********
Environment
***********

.. include:: tutorial_environment_activation.txt

*******************
Directory Structure
*******************

3. Create a directory ``tutorial_04_simulation`` in the ``waves-eabm-tutorial`` directory.

.. code-block:: bash

   $ pwd
   /path/to/waves-eabm-tutorial
   $ mkdir tutorial_04_simulation

4. Copy the ``tutorial_03_solverprep/SConscript`` file into the newly created ``tutorial_04_simulation``
   directory.

.. code-block:: bash

   $ pwd
   /path/to/waves-eabm-tutorial
   $ cp tutorial_03_solverprep/SConscript tutorial_04_simulation/


.. _tutorial_simulation_waves_SConscript:

**********
SConscript
**********

.. note::

    There is a large section of lines in the ``SConscript`` file that are not included before the next section of code 
    shown here, as they are identical to those from :ref:`tutorial_solverprep_waves`. The ``diff`` of the ``SConscript`` 
    file at the end of the :ref:`tutorial_solverprep_waves_SConscript` section will demonstrate this more clearly.

5. Modify your ``tutorial_04_simulation/SConscript`` file by adding the contents shown below immediately after the code 
   pertaining to ``# SolverPrep`` from the previous tutorial.

.. admonition:: waves-eabm-tutorial/tutorial_04_simulation/SConscript

    .. literalinclude:: tutorial_04_simulation_SConscript
       :language: Python
       :lineno-match:
       :start-after: marker-1
       :end-before: marker-2

A ``diff`` against the ``SConscript`` file from :ref:`tutorial_solverprep_waves` is included below to help identify the
changes made in this tutorial.

.. admonition:: waves-eabm-tutorial/tutorial_04_simulation/SConscript

   .. literalinclude:: tutorial_04_simulation_SConscript
      :language: Python
      :diff: tutorial_03_solverprep_SConscript

**********
SConstruct
**********

A ``diff`` against the ``SConstruct`` file from :ref:`tutorial_solverprep_waves` is included below to help identify the
changes made in this tutorial.

.. admonition:: waves-eabm-tutorial/SConstruct

   .. literalinclude:: eabm_tutorial_04_simulation_SConstruct
      :language: Python
      :diff: eabm_tutorial_03_solverprep_SConstruct

*************
Build Targets 
*************

5. Build the new targets

.. code-block:: bash

   $ pwd
   /path/to/waves-eabm-tutorial
   $ scons tutorial_04_simulation

************
Output Files
************
