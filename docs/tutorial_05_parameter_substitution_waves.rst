.. _tutorial_parameter_substitution_waves:

###################################
Tutorial 05: Parameter Substitution
###################################

**********
References
**********

* `Python Template Strings`_
* `Abaqus *PARAMETER`_ keyword documentation

***********
Environment
***********

.. include:: tutorial_environment_activation.txt

*******************
Directory Structure
*******************

3. Create a directory ``tutorial_05_parameter_substitution`` in the ``waves-eabm-tutorial`` directory.

.. code-block:: bash

   $ pwd
   /path/to/waves-eabm-tutorial
   $ mkdir tutorial_05_parameter_substitution

4. Copy the ``tutorial_04_simulation/SConscript`` file into the newly created ``tutorial_05_parameter_substitution``
   directory.

.. code-block:: bash

   $ pwd
   /path/to/waves-eabm-tutorial
   $ cp tutorial_04_simulation/SConscript tutorial_05_parameter_substitution/

******************
Solver Input Files
******************

5. Copy the ``eabm_package/abaqus/single_element_compression.inp`` file and all of its contents to a new file in the 
   same directory named ``single_element_compression.inp.in``. **Note:** the only change in the file name is the 
   addition of the ``.in`` suffix.

.. code-block:: bash

   $ pwd
   /path/to/waves-eabm-tutorial
   $ cp eabm_package/abaqus/single_element_compression.inp eabm_package/abaqus/single_element_compression.inp.in

In this tutorial, we will be modifying several scripts from :ref:`tutorial_simulation_waves`, the first of which is 
``single_element_compression.inp``. We copy this file and all of its contents to a new file with the same basename and 
the ``.in`` extension for the purposes of *parameter substitution*. This change is made so it is easy for the 
:meth:`waves.builders.copy_substitute` builder to identify which files should be searched for parameters. Any files with 
the ``.in`` extension that are passed to the :meth:`waves.builders.copy_substitute` builder will be parsed for 
characters matching the parameter definitions using substitution with `Python Template Strings`_. This is discussed in 
more detail later in this tutorial.

6. Use the ``diff`` below to modify your ``single_element_compression.inp.in`` file.

.. admonition:: waves-eabm-tutorial/eabm_package/abaqus/single_element_compression.inp.in
   
   .. literalinclude:: abaqus_single_element_compression.inp.in
      :language: text
      :diff: abaqus_single_element_compression.inp

First, we add the ``displacement`` parameter to the ``single_element_compression.inp.in`` file using the `Abaqus 
*PARAMETER`_ keyword. After making this definition, any place in the file that utilizes the ``<displacement>`` syntax 
will be replaced by the value ``float('@displacement@')`` by the Abaqus file parser. Casting the value substituted by 
the parameter to a ``float`` ensures that the ``displacement`` parameter ends up the proper variable type. This also 
eludes to the fact that a parameter can be any variable type, provided its usage is correct for the syntax of the file 
where it is used. Thus, for example, one could use a ``str`` as a parameter to change the name of the material assigned 
to a part in the model.

The final modification to make to the ``single_element_compression.inp.in`` file is to replace the hardcoded 
displacement value of ``-1.0`` with the parameter key ``<displacement>``. With this change, the Abaqus file parser will 
know to use the value of the ``displacement`` parameter anywhere it sees ``<displacement>``.

**********
SConscript
**********

7. Modify your ``tutorial_05_parameter_substitution/SConscript`` file by adding the contents shown below to the code 
   pertaining to ``# Simulation variables``. The entire code snippet shows how your code should look after editing, and
   the highlghted portion is what needs to be added to your existing code.
   
.. admonition:: waves-eabm-tutorial/tutorial_05_parameter_substitution/SConscript
   
   .. literalinclude:: tutorial_05_parameter_substitution_SConscript
      :language: Python
      :lineno-match:
      :start-after: marker-1
      :end-before: marker-2
      :emphasize-lines: 3-9

In the code you just added, a ``simulation_variables`` dictionary is defined. Each key-value pair in the 
``simulation_variables`` dictionary defines a parameter that already exists in several of the scripts we have utilized 
in the previous tutorials. ``width`` and ``height`` are used in the ``single_element_geometry.py`` and 
``single_element_partition.py`` scripts, and ``global_seed`` is used in the ``single_element_mesh.py`` script. Recall 
that each of these scripts is called using a command line interface that has default parameters. See the 
:ref:`sphinx_cli` to see what the default values are. As mentioned in :ref:`tutorial_geometry_waves`, the argument 
parser for each of these scripts will supply a default value for each command line argument that is not specified 
(assuming a defualt value was specified in the argument parser definition). This allowed us to simplify the command 
passed to the :meth:`waves.builders.abaqus_journal` builder. The advantage to coding this behavior ahead of time is that 
we get parameter substitution into our journal files for free. The ``width``, ``height``, and ``global_seed`` keys of 
the ``simulation_variables`` dictionary will be used later in this tutorial to specify the values passed to the journal 
files via the CLI.

The final key-value pair defined in the ``simulation_variables`` dictionary is ``displacement``. This parameter will be 
used in a slightly different way than the others, as the script that utilizes this parameter does not function with a 
command line interface. Recall from earlier in this tutorial, we created a new file called 
``single_element_compression.inp.in`` and added an `Abaqus *PARAMETER`_ definition with the ``@displacement@`` key. 
Here, our final key-value pair of the ``simulation_variables`` dictionary will be utlized. Disussion of exacly how this 
is implemented with the :meth:`waves.builders.copy_substitute` builder will come later in this tutorial.

Finally, we must discuss the last line of your new code, which defines the ``simulation_substitution_dictionary``. 
Simply put, the keys of the ``simulation_variables`` dictionary must be uniquely identifiable as parameters in the midst 
of all the other text in a file. Note that this step is only required when utilizing the 
:meth:`waves.builders.copy_substitute` builder for parameter substitution. In the code you will add next, we will 
continue to use the ``simulation_variables`` dictionary, as we do not need uniquely identifiable parameter keys when 
values are passed to our scripts via command line interface.

8. Modify your ``tutorial_05_parameter_substitution/SConscript`` file by using the highlighed lines below to modify the 
   ``journal_options`` for the code pertaining to ``# Geometry``, ``# Partition``, and ``# Mesh``.

.. admonition:: waves-eabm-tutorial/tutorial_05_parameter_substitution/SConscript

   .. literalinclude:: tutorial_05_parameter_substitution_SConscript
      :language: Python
      :lineno-match:
      :start-after: marker-3
      :end-before: marker-4
      :emphasize-lines: 3, 11, 19

As was previously discussed, we use the key-value pairs of the ``simulation_variables`` dictionary in the arguments we 
pass to the command line interfaces for ``single_element_{geometry,partition,mesh}.py``. Using a formatted string as 
shown in the first highlighted section, we will end up passing a string that looks like the following to the 
``single_element_geometry.py`` CLI:

.. code-block:: python
    
   journal_options = "--width 1.0 --height 1.0"

This behavior is repeated for the code pertaining to ``# Partition`` and ``# Mesh``.

9. Modify your ``tutorial_05_parameter_substitution/SConscript`` file by using the highlighed lines below to modify the 
   code pertaining to ``# SolverPrep``.

.. admonition:: waves-eabm-tutorial/tutorial_05_parameter_substitution/SConscript

   .. literalinclude:: tutorial_05_parameter_substitution_SConscript
      :language: Python
      :lineno-match:
      :start-after: marker-4
      :end-before: marker-5
      :emphasize-lines: 3, 13-14

Per the changes you made earlier in this tutorial, the ``abaqus_source_list`` must be updated to reflect the replacement 
of ``single_element_compression.inp`` with the parameterized ``single_element_compression.inp.in`` file.

The final change to be made in the ``tutorial_05_parameter_substitution/SConscript`` file is to utilize the 
``substitution_dictionary`` parameter in the usage of the :meth:`waves.builders.copy_substitute` builder. This builder 
uses template substitution on files named with the ``*.in`` extension, and looks to match and replace *any characters* 
that match the keys in the provided ``substitution_dictionary``. For this reason, we must make our parameter names 
uniquely identifiable (e.g. ``@variable@``).

In summary of the changes you just made to the ``tutorial_05_parameter_substitution`` file, a ``diff`` against the 
``SConscript`` file from :ref:`tutorial_simulation_waves` is included below to help identify the
changes made in this tutorial.

.. admonition:: waves-eabm-tutorial/tutorial_05_parameter_substitution/SConscript

   .. literalinclude:: tutorial_05_parameter_substitution_SConscript
      :language: Python
      :diff: tutorial_04_simulation_SConscript

**********
SConstruct
**********

10. Add ``tutorial_05_parameter_substitution`` to the ``eabm_simulation_directories`` list in the 
    ``waves-eabm-tutorial/SConstruct`` file.

A ``diff`` against the ``SConstruct`` file from :ref:`tutorial_simulation_waves` is included below to help identify the
changes made in this tutorial.

.. admonition:: waves-eabm-tutorial/SConstruct

   .. literalinclude:: eabm_tutorial_05_parameter_substitution_SConstruct
      :language: Python
      :diff: eabm_tutorial_04_simulation_SConstruct

*************
Build Targets 
*************

11. Build the new targets

.. code-block:: bash

   $ pwd
   /path/to/waves-eabm-tutorial
   $ scons tutorial_05_parameter_substitution

************
Output Files
************

Explore the contents of the ``build`` directory using the ``tree`` command against the ``build`` directory, as shown 
below. Note the usage of the ``-I`` option to reduce clutter in the ``tree`` command output.

.. code-block:: bash
    
    $ pwd
    /home/roppenheimer/waves-eabm-tutorial
    $ tree build/ -I 'tutorial_0[1,2,3,4]*'
