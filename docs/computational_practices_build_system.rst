.. _build_system:

************
Build System
************

.. note:: Related curriculum

   Software Carpentry: SCons-Novice - https://carpentries-incubator.github.io/scons-novice/
   :cite:`SoftwareCarpentry,swc-scons`

.. _build_system_directed_graphs:

Directed graphs
---------------

At their core, the majority of software build systems provide two features: `directed acyclic graph`_ (DAG) construction
and automated task execution according to that DAG. Modern software projects are often composed from a large number of
source files with complex file and library interactions. Consequently, determining the build order and executing the
build process is a complex and error-prone task. Build systems provide a solution for automating the construction and
execution of the build DAG to reduce build errors and inconsistencies. In addition to the DAG construction and
execution, most build systems will also provide a feature to avoid unnecessary re-execution for portions of the DAG that
haven't changed since the last execution.

Many engineering simulation projects suffer from similar complexity in simulation construction, where the geometry of
many separate parts must be created or defeatured from existing files, partitioned for meshing, meshed, and linked to
simulation boundary and loading conditions. These tasks may be interconnected, where one part's partitioning depends on
another part's mesh. After executing a simulation, there may be a similarly complex post-processing workflow. When this
process is repeated many times, as in parameter studies, it is desirable to enable programmatic execution of the
workflow because manual processes do not scale and are prone to consistency errors. Even in the case where this process
is not executed programmatically on a regular basis, a manual process will be error-prone and difficult to document.

Build systems are able to construct directed graphs from task definitions. Each task is defined by the developer and
subsequently linked by the build system. Tasks are composed of targets, sources, and actions. A target is the output of
the task. Sources are the required direct-dependency files used by the task and may be files tracked by the version
control system for the project or files produced by other tasks. Actions are the executable commands that produce the
target files. In pseudocode, this might look like a dictionary:

.. code-block:: YAML

   task1:
       target: output1
       source: source1
       action: action1 --input source1 --output output1

   task2:
       target: output2
       source: output1
       action: action2 --input output1 --output output2

As the number of discrete tasks increases, and as cross-dependencies grow, an automated tool to construct the build
order becomes more important.

Task definitions go by different names in different build systems, such as "rule" in `GNU Make`_ :cite:`gnu-make` or
"task" in `SCons`_ :cite:`SCons`. Task definitions may be simplified for common actions by "pattern rules" in GNU Make
or "Builders" in SCons, which may associate a particular file extension with a predefined action or auto-generate a
target file name that matches the source file name. Build systems usually provide a set of common patterns for compiling
different programming languages.

For the purpose of executing simulations, it is important to use a build system that allows developers to write custom
task generators for the numeric solvers and post-processing programs used in the project. `WAVES`_ contains a collection
of `SCons`_ custom builders for common engineering simulation software packaged for reuse by many projects.  However,
it is likely that engineers will need to become familiar with their build system's task definition syntax to support the
wide array of engineering software available for use.

Task definitions and task generators help engineering simulation developers to use build systems designed for software
compilation. Breaking an engineering pre-processing, simulation, and post-processing workflow into small unit tasks can
maximize the effectiveness of using a build system but may require a deeper look at existing workflows to determine how
to break the workflow up in a suitable way.

There are trade-offs to workflow granularity that will depend on the needs of the current simulation or simulation suite
in a :term:`modsim repository`, so a prescriptive process for performing this work may be difficult to develop. A
generic template for a finite element simulation workflow is included in the `WAVES`_ :ref:`user_manual` and has proved
to be a good starting point in practice for production-engineering analysis.

The benefit of adopting a build system workflow is the automated DAG construction and execution, but most build
systems, including `GNU Make`_ and `SCons`_, also provide conditional rebuilding where only the portion of the workflow
that has changed is executed. This is valuable when, for instance, a new post-processing filter should be applied to
simulation results, but the simulations do not need to be rerun.

Without any manual intervention or manual dependency reconstruction, the same build command that launched the original
workflow can be executed again, and the build system will determine what portions of the workflow need to be executed for
the new task definitions. Similarly, for a suite of simulations managed by a build system, if one input file of many
files is changed, only those simulations that depend on the updated input file will be rerun.

Parameter studies
-----------------

Besides the difference in task definitions, another reason that build systems may not be an obvious choice for
computational engineering simulation and analysis control is the practice of running parameter studies. In computational
engineering, a parameter study is composed of many parameter sets. The parameter sets themselves are typically small
variations on input variable values, which do not change the overall workflow.

At face value, parameter studies are most closely related to "build configurations" of software build systems, where the
software may be compiled with different options for a debugging build (as opposed to the final release build). Unlike
engineering parameter studies, software build systems are generally designed to produce a single build configuration at
a time. This makes the build configuration features of a build system difficult to apply to the execution of
engineering-parameter studies.

Another way to interpret a parameter study is that the parameter sets are targets of a parameter-study generation task.
These parameter set files could then be used as the sources for a common workflow repeated for each parameter set.  The
ability to conditionally rebuild only those sets that are new or changed when the parameter study definition changes is
appealing.

However, most build systems split the DAG construction and execution into exactly two steps: configuration and
execution. The DAG is first constructed during the build system's configuration stage. At this stage, the DAG must be
fully known. Having fixed the DAG, the execution phase will execute the workflow. If the parameter study is created as a
task that is executed as part of the build, the DAG will not reconfigure mid-build to account for the workflow
repetition of each parameter set. This approach may work if the number of parameter sets is known or fixed as part of
the task definitions, but it is not robust against changing the parameter study size.

A more robust solution is to perform the parameter study generation at configuration time such that the repeated
workflow can create task nodes in the DAG prior to the execution phase. A similar configuration-time workflow is not
common to software build system guides, so adopting this solution is not immediately obvious. This solution may also
require the configuration-time parameter generation tool to perform its own conditional rebuilding logic for any
parameter set files that are produced.

The `WAVES`_ package includes a collection of command-line utilities and Python modules to aid in adopting software
build systems for engineering workflows. The `WAVES`_ parameter generator command-line interface(s) are designed to work
with most build systems, but were originally developed with the requirements of `CMake`_ in mind.

The `WAVES`_ :ref:`user_manual` focuses on extending the build system `SCons`_ because `SCons`_ configuration files use
`Python`_ as a fully featured scripting language. This choice is primarily driven by the familiarity of the engineering
community with `Python`_ as a programming language. Using Python as the build-system scripting language also means the
parameter-generation utility can be integrated more closely with the build system, :ref:`parameter_generator_api`.
