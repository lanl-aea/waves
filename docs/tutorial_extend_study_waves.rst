.. _tutorial_extend_study_waves:

#########################################
Automatically Extending a Parameter Study
#########################################

.. warning::

   The ``waves build`` feature is considered experimental. The feature should be treated like an alpha feature whose
   design, behavior, and interface may change without notice. This feature is documented to solicit user feedback on
   preferred behavior and usefulness.

.. include:: wip_warning.txt

.. TODO: remove the scipy minimum version note after requiring scipy>=1.7.0 in Conda package runtime requirements
.. https://re-git.lanl.gov/aea/python-projects/waves/-/issues/278

.. warning::

   The `AEA Compute environment`_ ``aea-{release,beta}`` does not yet support ``scipy>=1.7.0`` :issue:`278`. This
   tutorial can only be completed in a user-created environment. `WAVES`_ is available on the `AEA Conda channel`_.

**********
References
**********

* :ref:`waves_cli` :ref:`waves_build_cli` subcommand
* |PROJECT| :ref:`parameter_generator_api` API: :meth:`waves.parameter_generators.SobolSequence`
* `Xarray`_ and the `xarray dataset`_ :cite:`xarray,hoyer2017xarray`

***********
Environment
***********

.. include:: tutorial_environment_activation.txt

*******************
Directory Structure
*******************

3. Create a directory ``tutorial_extend_study`` in the ``waves-eabm-tutorial`` directory.

.. code-block:: bash

   $ pwd
   /path/to/waves-eabm-tutorial
   $ mkdir tutorial_extend_study

4. Copy the ``tutorial_07_sobol_sequence`` file into the newly created ``tutorial_extend_study``
   directory.

.. code-block:: bash

   $ pwd
   /path/to/waves-eabm-tutorial
   $ cp tutorial_07_sobol_sequence tutorial_extend_study

**********
SConscript
**********

A ``diff`` against the ``SConscript`` file from :ref:`tutorial_cartesian_product_waves` is included below to help identify the
differences between the two parameter generators.

.. admonition:: waves-eabm-tutorial/tutorial_extend_study

   .. literalinclude:: tutorials_tutorial_extend_study
      :language: Python
      :diff: tutorials_tutorial_07_sobol_sequence

**********
SConstruct
**********

A ``diff`` against the ``SConstruct`` file from :ref:`tutorial_cartesian_product_waves` is included below to help identify the
changes made in this tutorial.

.. admonition:: waves-eabm-tutorial/SConstruct

   .. literalinclude:: tutorials_tutorial_extend_study_SConstruct
      :language: Python
      :diff: tutorials_tutorial_07_sobol_sequence_SConstruct

*************
Build Targets
*************

5. Build the new targets

.. code-block:: bash

   $ pwd
   /path/to/waves-eabm-tutorial
   $ waves build --max-iterations=4 tutorial_extend_study --jobs=4

************
Output Files
************

.. code-block:: bash

   $ pwd
   /path/to/waves-eabm-tutorial
   $ tree build/tutorial_extend_study -d
   build/tutorial_extend_study
   |-- parameter_set0
   |-- parameter_set1
   |-- parameter_set2
   |-- parameter_set3
   |-- parameter_set4
   |-- parameter_set5
   |-- parameter_set6
   `-- parameter_set7

   8 directories
