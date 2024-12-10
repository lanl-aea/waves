.. _tutorial_sensitivity_study:

###########################
Tutorial: Sensitivity Study
###########################

**********
References
**********

* `numpy.corrcoef`_ :cite:`numpy`
* `SALib.analyze`_ :cite:`salib`
* `seaborn.pairplot`_ :cite:`seaborn`

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

    .. code-block:: bash

        $ pwd
        /home/roppenheimer/waves-tutorials
        $ waves fetch --overwrite --tutorial 12 && mv tutorial_12_archival_SConstruct SConstruct
        WAVES fetch
        Destination directory: '/home/roppenheimer/waves-tutorials'

4. Download and copy the ``tutorial_12_archival`` file to a new file named ``tutorial_sensitivity_study`` with the
   :ref:`waves_cli` :ref:`waves_fetch_cli` subcommand.

.. code-block:: bash

   $ pwd
   /home/roppenheimer/waves-tutorials
   $ waves fetch --overwrite tutorials/tutorial_12_archival && cp tutorial_12_archival tutorial_sensitivity_study
   WAVES fetch
   Destination directory: '/home/roppenheimer/waves-tutorials'

********************
Parameter Study File
********************

5. Create a new file ``modsim_package/python/rectangle_compression_sensitivity_study.py`` from the content below.

.. admonition:: waves-tutorials/modsim_package/python/rectangle_compression_sensitivity_study.py

   .. literalinclude:: python_rectangle_compression_sensitivity_study.py
      :language: Python

This file should look similar to the parameter study file in :ref:`tutorial_sobol_sequence`; however, this tutorial uses
the SALib :cite:`salib` based parameter generator :meth:`waves.parameter_generators.SALibSampler` instead of the SciPy
:cite:`scipy` based parameter generator :meth:`waves.parameter_generators.SobolSequence`. Both SALib and SciPy are good
packages for generating samples and post-processing data, but this tutorial will use SALib for the sensitivity analysis
post-processing workflow so the tutorial will generate samples with the matching package. It is not always necessary to
match the sample generator to the sensitivity analysis tools, but some analysis solutions are sensitive to the sample
generation algorithm. Readers are encouraged to review both packages to match the sample generation and analysis
strategy to their needs.

**********
SConscript
**********

A ``diff`` against the ``tutorial_12_archival`` file from :ref:`tutorial_archival` is included below to help identify
the changes made in this tutorial.

.. admonition:: waves-tutorials/tutorial_sensitivity_study

   .. literalinclude:: tutorials_tutorial_sensitivity_study
      :language: Python
      :diff: tutorials_tutorial_12_archival

**********************
Post-processing script
**********************

6. In the ``waves-tutorials/modsim_package/python`` directory, create a file called ``sensitivity_study.py`` using the
   contents below.

.. admonition:: waves-tutorials/modsim_package/python/sensitivity_study.py

   .. literalinclude:: python_sensitivity_study.py
      :language: Python

This file should look similar to the ``post_processing.py`` file from :ref:`tutorial_post_processing`. Unused functions
have been removed and the output has changed to reflect the sensitivity study operations. In practice, modsim projects
should move the shared functions of both post-processing scripts to a common utilities module.

Unlike :ref:`tutorial_post_processing`, the sensitivity study script does require the parameter study file. It is not
possible to calculate the sensitivity of output variables to input variables without associating output files with their
parameter set. After merging the output datasets with the parameter study, the correlation coefficients can be plotted
with seaborn :cite:`seaborn`. Numpy :cite:`numpy` is used to perform a similar correlation coefficients calculation that
can be saved to a CSV file for further post-processing or regression testing as in :ref:`tutorial_regression_testing`.
Finally, SALib :cite:`salib` is used to perform a delta moment-independent analysis, which is compatible with all SALib
sampling techniques.

The value of processing output data into an Xarray :cite:`xarray` dataset is evident here, where each new plotting
and analysis tool requires data in a slightly different form factor. For these tutorials, WAVES provides an extraction
utility to process simulation output data into an Xarray dataset. However, it is well worth the modsim owner's time to
seek out or write similar data serialization utilities for all project numeric solvers. Beyond the ease of
post-processing, tightly coupled and named column data structures reduce the chances of post-processing errors during
data handling operations.

While the post-processing approach outlined in this tutorial gives users a starting point for performing all forms of
parameter studies (sensitivity, perturbation, uncertainty propagation, etc) the choice of input sampling tools,
parameter sampling ranges and distributions, and analysis tools is highly dependent on the needs of the project and the
characteristics of the input space and numerical solvers. Modsim project owners are encouraged to read the sampling and
analysis documentation closely and seek advice from statistics and uncertainty experts in building and interpreting
their parameter studies.

**********
SConstruct
**********

7. Update the ``SConstruct`` file. A ``diff`` against the ``SConstruct`` file from :ref:`tutorial_archival` is included
   below to help identify the changes made in this tutorial.

.. admonition:: waves-tutorials/SConstruct

   .. literalinclude:: tutorials_tutorial_sensitivity_study_SConstruct
      :language: Python
      :diff: tutorials_tutorial_12_archival_SConstruct

*************
Build Targets
*************

8. Build the new sensitivity study targets

.. code-block:: bash

   $ pwd
   /home/roppenheimer/waves-tutorials
   $ scons tutorial_sensitivity_study --jobs=4
   <output truncated>

************
Output Files
************

Explore the contents of the ``build`` directory using the ``tree`` command against the ``build`` directory, as shown
below. Note that the output files from the previous tutorials may also exist in the ``build`` directory, but the
directory is specified by name to reduce clutter in the output shown.

.. code-block:: bash

   $ pwd
   /home/roppenheimer/waves-tutorials
   $ tree build/tutorial_sensitivity_study/ -L 1
   build/tutorial_sensitivity_study/
   |-- correlation_pairplot.pdf
   |-- parameter_set0
   |-- parameter_set1
   |-- parameter_set10
   |-- parameter_set11
   |-- parameter_set12
   |-- parameter_set13
   |-- parameter_set14
   |-- parameter_set15
   |-- parameter_set16
   |-- parameter_set17
   |-- parameter_set18
   |-- parameter_set19
   |-- parameter_set2
   |-- parameter_set3
   |-- parameter_set4
   |-- parameter_set5
   |-- parameter_set6
   |-- parameter_set7
   |-- parameter_set8
   |-- parameter_set9
   |-- parameter_study.h5
   |-- sensitivity.yaml
   |-- sensitivity_study.csv
   `-- sensitivity_study.csv.stdout

   20 directories, 5 files

The purpose of the sensitivity study is to observe the relationships between the input space parameters (width and
height) on the output space parameters (peak stress). The script writes a correlation coefficients plot relating each
input and output space parameter to every other parameter.

.. figure:: tutorial_sensitivity_study_sensitivity_study.png
   :align: center
   :width: 100%
   :name: tutorial_sensitivity_analysis_correlation_coefficients

   Correlation coefficients

In the :ref:`tutorial_sensitivity_analysis_correlation_coefficients` figure we can see both the input and output
histograms on the diagonal. The scatter plots show the relationships between parameters. We can see very little
correlation between the stress output and the width input, and strongly linear correlation between the stress output and
the height input.  This is the result we should expect because we are applying a fixed displacement load and stress is
linearly dependent on the applied strain, which is a function of the change in displacement and the unloaded height. If
we were instead applying a force, we should expect the opposite correlation because stress would then depend on the
applied load divided by the cross-sectional area.

.. raw:: latex

   \FloatBarrier
