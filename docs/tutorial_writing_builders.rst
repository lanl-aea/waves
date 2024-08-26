.. tutorial_writing_builders:

##########################
Tutorial: Writing Builders
##########################

This tutorial will introduce |PROJECT| style builders using the
:meth:`waves.scons_extensions.first_target_builder_factory` with considerations for handling some representative types
of numeric solver behavior. For an example of writing more generic `SCons Builders`, see the `SCons`_ user manual
:cite:`scons-user`. For a quickstart with simple builders that mimic the |PROJECT| builder directory change operations,
see the :ref:`scons_quickstart`.

**********
References
**********

* `SCons Builders`_ :cite:`scons-user`
* :ref:`scons_quickstart`

***********
Environment
***********

.. include:: tutorial_environment_activation.txt

.. include:: version_check_warning.txt

*******************
Directory Structure
*******************

3. Create a new ``tutorial_writing_builders`` directory with the ``waves fetch`` command below

.. code-block:: bash

   $ pwd
   /home/roppenheimer/waves-tutorials
   $ waves fetch --destination tutorial_writing_builders tutorials/tutorial_writing_builders
   $ ls tutorial_writing_builders
   SConstruct implicit.yaml implicit_workflow scons_extensions.py solver test_scons_extensions.py

******
Solver
******

Before writing a builder, it is important to understand the solver's file handling behaviors, exit behaviors, and
command line interface options. The specific nature of the numeric algorithms and solution procedures are important
considerations when choosing a solver, but when writing a builder only the interfaces with the file system and shell are
important. To write a robust builder, you need four things from the solver

1. Deterministic output file paths *at workflow configure time*
2. Well defined exit criteria
3. Command line options for non-interactive behavior control
4. Non-interactive output file overwrite control options

It is also helpful for the solver to provide

5. Complete control over all output file paths and file base names, including logs

Deterministic output file paths are necessary to allow builder users to define targets for downstream task consumption.
While it is possible to write a builder based on :meth:`waves.scons_extensions.first_target_emitter` that does not track
any solver owned output files, such a builder is difficult to robustly integrate in a workflow. If solver output file
paths are non-deterministic *at workflow configure time* or difficult to control from the CLI, it is still possible to
write a builder by tracking the STDOUT and STDERR messages and redirecting them to a task-specific ``*.stdout`` file.
However, this pushes more effort of workflow configuration onto end users of the builder. If all or some output file
paths can be determined at configure time it is possible to write an associated `SCons Emitters`_ to automatically
populate known builder targets.

Well defined exit criteria is necessary to return reliable task states on solver failures and successes. Most builders
should avoid modifying the default solver behavior to provide users with the documented, and therfore expected,
behavior. However, when solvers under report non-zero exit codes for fatal errors, false positives, it may be necessary
to do extra work, such as log file inspection, to return more reliable exit codes and avoid attempting downstream tasks
when the solver task is known to have failed. This is especially important when the solver writes partial output results
that may propagate false positives further down the workflow. False negatives can be equally frustrating when the solver
results files are sufficiently complete for the user's workflow and should not be considered fatal. Because desirable
task outcome behavior is often project or even workflow specific, it is usually best to maintain the documented solver
behavior when writing builders for general distribution.

Command line options for non-interactive behavior control are necessary to provide automatic execution of large
workflows and parametric studies. A large benefit of using build systems is providing consistent, reproducible behavior.
This is much more difficult when when interactive controls allow workflow behavioral changes. Additionally, interactive
controls do not scale well. Finally, when using the :meth:`waves.scons_extensions.first_target_builder_factory` and
associated :meth:`waves.scons_extensions.first_target_emitter`, the solver STDOUT and STDERR are redirected to a
task-specific log file to provide at least one target file and make task-specific trouble-shooting less cumbersome. It
is possible to modify the builder factory's redirection operation to simultaneously stream to STDOUT/STDERR and a
redirected task log file; however, the commands implementing such behavior are not common to all operating systems and
shells and is therefore best left to the end user and project specific needs. As a default, a less cluttered STDOUT is
often more useful for end users tracking workflow execution, too.

Output overwrite controls are important when writing builders. If the solver increments output file names, workflow
re-execution will create file system state dependent targets. Technically these may be deterministic at configure time.
However, as a practical matter these are difficult to predict and functionally non-deterministic from the perspective of
the builder author because they may depend on the end user's task construction. If the solver provides an option to
overwrite a deterministic output file name, the builder and any associated emitter are much easier to write and test for
completeness.

If the output files are controllable and deterministic, then it is possible to work around a missing overwrite feature
by adding a pre-solver action that performs file system cleanup as part of the builder. Writing a multi-action builder
is outside the scope of the current tutorial, but there are examples in :ref:`scons_multiactiontask` and the
:meth:`waves.scons_extensions.action_list_strings` and :meth:`waves.scons_extensions.action_list_scons` functions can
help advanced users pull apart existing builders to augment the action list.

The placeholder solver used in this tutorial does no real work, but provides some common output handling use cases as
examples for considerations in builder design. As seen in the solver documentation below, the solver writes a log file
with no path controls and no overwrite behavior. The solver builder can not reliably manage this file, except to change
to the target parent directory prior to solver execution to ensure that the log is co-located with other task output
files. The output file names are deterministic, but require task specific knowledge of the solver options. As a first
draft, the builder will make no attempt to predict output file names and instead rely on the user's knowledge of solver
behavior and task options to write complete target lists. There is an overwrite option, which the builder will require
to make task behavior more predictable. There is no interactive behavior to work around and also no CLI option to force
non-interactive behavior.

Solver documentation
====================

.. automodule:: solver
    :noindex:
    :members:
    :show-inheritance:

**********
SConscript
**********

**********
SConstruct
**********

****************
Building targets
****************

************
Output Files
************

**********************
Workflow Visualization
**********************
