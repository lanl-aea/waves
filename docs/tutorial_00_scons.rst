##################
Tutorial 00: SCons
##################

*************
Prerequisites
*************

1. :ref:`computational_tools` :ref:`build_system`
2. Software Carpentry: GNU Make -  https://swcarpentry.github.io/make-novice/

***********
Environment
***********

***********
Description
***********

`WAVES`_ is a suite of build wrappers and command line utilities for the build system `SCons`_. Build systems help
automate the execution of complex computing workflows by constructing component task execution order. In the
`WAVES-EABM`_ tutorials, there are two components to the `SCons`_ configuration: project definition and simulation
definitions. This tutorial introduces the `SCons`_ project definition file for the `WAVES-EABM`_ template EABM
repository.

The command line utilities provided by `WAVES`_ are those utilities required to implement engineering workflows in
traditional software build systems. For most engineering simulation workflows, software build systems will work
out-of-the-box. However, it is difficult to implement engineering parameter studies in software build systems, which are
designed to produce a single program, not many nearly identical configurations of the same program. The `WAVES`_
parameter generator utility, (:ref:`parameter_study_cli`) are designed to work with most build systems, but were
originally developed with the requirements of `CMake`_ in mind.

For production engineering analysis, `WAVES`_ focuses on extending the build system `SCons`_ because `SCons`_
configuration files use `Python`_ as a fully featured scripting language. This choice is primarily driven by the
familiarity of the engineering community with `Python`_ as a programming language, but also because the parameter
generation utility can be integrated more closely with the build system, :ref:`parameter_generator_api`.

***************************
SCons Project Configuration
***************************

By convention, the `SCons`_ root project file is named ``SConstruct``. Because this is a `Python`_ file, we can import
`Python`_ libraries to help define project settings.

.. admonition:: SConstruct

   .. literalinclude:: ._SConstruct
      :language: Python
      :lineno-match:
      :end-before: marker-1
