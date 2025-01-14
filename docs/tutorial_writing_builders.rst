.. _tutorial_writing_builders:

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

* :ref:`scons_quickstart`
* `SCons Builders`_ :cite:`scons-user`
* `SCons AddPostAction`_ and `SCons AddPreAction`_ :cite:`scons-user`

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
   SConstruct implicit.yaml implicit_workflow pyproject.toml scons_extensions.py solver test_scons_extensions.py

4. Make the new ``tutorial_writing_builders`` directory the current working directory

.. code-block:: bash

   $ pwd
   /home/roppenheimer/waves-tutorials
   $ cd tutorial_writing_builders
   $ pwd
   /home/roppenheimer/waves-tutorials/tutorial_writing_builders
   $ ls tutorial_writing_builders
   SConstruct implicit.yaml implicit_workflow pyproject.toml scons_extensions.py solver test_scons_extensions.py

5. (Linux and MacOS only) Make the ``solver.py`` file executable. In a shell, use the command

   $ chmod +x solver.py

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

Normally the internal implementation and API are not accessible to solver users. Here, the full internal API is produced
as an example of Python command line utility and to allow users to play with solver behavior to more closely match
solvers of interest. While the Python implementation is written to |PROJECT| style and functional programming best
practices, the file handling behavior itself is undesirable when users have direct control over command line utility
behavior.

Solver documentation
====================

.. automodule:: solver
    :noindex:
    :members:
    :show-inheritance:

*******
Builder
*******

The tutorial's builder factory is written as a project specific Python module such that it could be documented and
packaged for distribution. It is also possible to write builder factories and builders directly into SCons configuration
files.

The builder itself is largely boilerplate documentation and a pass-through to the
:meth:`waves.scons_extensions.first_target_builder_factory`. Strictly speaking, the builder factory could be written
much more compactly by passing unchanged arguments through as ``*kwargs``. Hear, they are kept in the builder factory
definition to make documentation of the factory defaults easier and to explicitly set the defaults independently from
the |PROJECT| function.

Writing the entire builder from scratch would not require many extra lines of code. The use of the |PROJECT| function is
primarily to provide consistency with |PROJECT| builder factories. Builder factory authors are encouraged to read the
`SCons Builders`_ documentation when their solver needs are not met by the |PROJECT| template builder factories.

.. literalinclude:: tutorial_writing_builders_scons_extensions.py
   :language: Python
   :lineno-match:

Example unit tests to verify the builder action string, keywords, emitter, and node count are also provided. These are
similar to the |PROJECT| unit test verification suite for builder facotories based on
:meth:`waves.scons_extensions.first_target_builder_factory` and should be the minimum verification implemented for
similar builders.

Unit tests are not sufficient to verify desired solver behavior. System tests that run a real, but minimal, example
problem should also be implemented to ensure that the builder action string, task re-execution, file handling
expecations, and command line options are appropriate for workflow use. The system tests should be complete enough to
verify that the third-party solver behavior still matches the assumptions in the buider design. For |PROJECT|, the
tutorials serve as system tests for builder design. For a project specific builder, a minimal working example should be
included in the project as an inexpensive verification check and easy-to-use troubleshooting task.

.. literalinclude:: tutorial_writing_builders_test_scons_extensions.py
   :language: Python
   :lineno-match:

**********
SConscript
**********

The task target list depends on the solver options. The builder is not written to manage or inspect the solver command
line options and does not include an emitter to match the builder target expectations to the solver command line
options. Instead, the end user is expected to manage the target list directly.

As in many of the tutorials, the number of solve cpus is accepted from the project specific command line arguments. The
SConscript file implementing an implicit solver workflow inspects the construction environment solve cpus option prior
to configuring the task to determine the expected target list. Since the solver overrides the output file extension, no
special handling of the ``--output-file`` option is required to truncate or correct the provided extension when the
target list changes.

Since the solver does not provide any overwrite behavior for the log file, a user owned clean options is provided to
clean the entire workflow build directory in addition to the known target list. This is necessary to help workflow users
purge log files and to avoid solver task failures when the maximum number of log files is reached. More advanced
builder authors might choose to implement a log file clean action prior to the solver action. More advanced end users
might prefer to use an `SCons AddPreAction`_ to perform log file cleaning even when the builder does not. Without either
implementation, users must remember to clean their build directory regularly to avoid solver exits from accumulated log
files.

.. literalinclude:: tutorial_writing_builders_implicit_workflow
   :language: Python
   :lineno-match:

**********
SConstruct
**********

The SConstruct file of this tutorial is a stripped down example of the core tutorials. All features of the project
configuration should look familiar to the core tutorials. It implements a variant build directory, solve cpus control,
and environment recovery from the launching shell. Since the solver behaves like a project specific file, the solver
executable is found by absolute path from the tutorial/project directory and the parent directory is added to the
environment ``PATH``. Besides the default action construction, the project adds a project-specific solver option and the
``solve_cpus`` task keyword argument.

.. literalinclude:: tutorial_writing_builders_SConstruct
   :language: Python
   :lineno-match:

****************
Building targets
****************

First, run the workflow with the default number of solve cpus and observe the output directory.

.. code-block::

   $ scons implicit_workflow
   scons: Reading SConscript files ...
   Checking whether /home/roppenheimer/waves-tutorials/tutorial_writing_builders/solver.py program exists.../home/roppenheimer/waves-tutorials/tutorial_writing_builders/solver.py
   scons: done reading SConscript files.
   scons: Building targets ...
   cd /home/roppenheimer/waves-tutorials/tutorial_writing_builders/build/implicit_workflow && solver.py implicit --input-file /home/roppenheimer/waves-tutorials/tutorial_writing_builders/implicit.yaml --output-file=/home/roppenheimer/waves-tutorials/tutorial_writing_builders/build/implicit_workflow/implicit.out --overwrite --solve-cpus=1 > /home/roppenheimer/waves-tutorials/tutorial_writing_builders/build/implicit_workflow/implicit.out.stdout 2>&1
   scons: done building targets.
   $ find build -type f
   build/implicit_workflow/implicit.out
   build/implicit_workflow/implicit.out.stdout
   build/implicit_workflow/solver.log

Re-run the workflow with two solve cpus. The task re-runs because the target list has changed. With the target list
change, the original, single cpu solve output file is left around and not overwritten. A more advanced builder or user
task definition is required to clean up previous files when the expected target file list changes. If the solver or
builder factory provided an option to merge the multiple cpu output files, it could be possible for the user to write a
task that does not re-execute when the number of solve cpus changes. In this tutorial, the user would need to write the
merge operation as an `SCons AddPostAction`_ to get similar behavior when the requested solver cpus changed.

Observe that the previous log file still exists and a new log file with extension ``*.log1`` is found in the build
output. Cleaning log files to produce deterministic output for task log file tracking and cleaning would require a more
advanced user task definition. It would be tempting to write a builder action that always purges log files prior to
execution; however, if the end user were running multiple solver tasks in this build directory, all log files of
previous tasks would also be removed. In this case, it is probably better to leave log file handling to the end user.

Finally, the user target list construction combined with the builder ``--output-file`` option handling results in the
``*.stdout`` file name change from ``implicit.out.stdout`` to ``implicit.out0.stdout``. A builder factory emitter could
be written to look for the ``solve_cpus`` environment varible to match emitted solver output targets to solver output
handling. Changing the ``*.stdout`` naming convention for greater consistency is possible to handle in the builder
factory, but would be more difficult to implement robustly and document clearly, so matching the extension of the first
expected target is probably best.

.. code-block::

   $ scons implicit_workflow --solve-cpus=2
   scons: Reading SConscript files ...
   Checking whether /home/roppenheimer/waves-tutorials/tutorial_writing_builders/solver.py program exists.../home/roppenheimer/waves-tutorials/tutorial_writing_builders/solver.py
   scons: done reading SConscript files.
   scons: Building targets ...
   cd /home/roppenheimer/waves-tutorials/tutorial_writing_builders/build/implicit_workflow && solver.py implicit --input-file /home/roppenheimer/waves-tutorials/tutorial_writing_builders/implicit.yaml --output-file=/home/roppenheimer/waves-tutorials/tutorial_writing_builders/build/implicit_workflow/implicit.out0 --overwrite --solve-cpus=2 > /home/roppenheimer/waves-tutorials/tutorial_writing_builders/build/implicit_workflow/implicit.out0.stdout 2>&1
   scons: done building targets.
   $ find build -type f
   build/implicit_workflow/implicit.out0
   build/implicit_workflow/implicit.out
   build/implicit_workflow/solver.log1
   build/implicit_workflow/implicit.out1
   build/implicit_workflow/implicit.out.stdout
   build/implicit_workflow/implicit.out0.stdout
   build/implicit_workflow/solver.log

Run the clean operation with the two solve cpus option and observe that the entire builder directory is removed. This is
necessary for the end user to have consistent log file purging behavior without resorting to shell remove commands.
Removing build directory artifacts by shell command is not necessarily a bad practices, but can build up muscle memory
for commands that are unnecessarily destructive, such as removing the entire build directory with ``rm -r build``. In a
single workflow project like this tutorial this achieves the same result. But in a project with many or computationally
expensive workflows this muscle memory may result in expensive data loss and ``scons workflow --clean`` operations
should be preferred, but not relied upon, for better data retention habits.

.. code-block::

   $ scons implicit_workflow --solve-cpus=2 --clean
   scons: Reading SConscript files ...
   Checking whether /home/roppenheimer/waves-tutorials/tutorial_writing_builders/solver.py program exists.../home/roppenheimer/waves-tutorials/tutorial_writing_builders/solver.py
   scons: done reading SConscript files.
   scons: Cleaning targets ...
   Removed build/implicit_workflow/implicit.out0
   Removed build/implicit_workflow/implicit.out1
   Removed build/implicit_workflow/implicit.out0.stdout
   Removed build/implicit_workflow/implicit.out
   Removed build/implicit_workflow/implicit.out.stdout
   Removed build/implicit_workflow/solver.log
   Removed build/implicit_workflow/solver.log1
   Removed directory build/implicit_workflow
   scons: done cleaning targets.
   $ find build -type f
   $
