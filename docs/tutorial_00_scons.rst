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

.. include:: eabm_README.txt
   :start-after: env-start-do-not-remove
   :end-before: env-end-do-not-remove

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

1. Create and change to a new project root directory to house the tutorial files. For example

   .. code-block:: bash

      $ pwd
      /home/roppenheimer
      $ mkdir waves-eabm-tutorial
      $ cd /home/roppenheimer/waves-eabm-tutorial

2. Create a new file named ``SConstruct`` in the ``waves-eabm-tutorial`` directory with the contents listed below. Note
   that the filename is case sensitive.

.. admonition:: SConstruct

   .. code-block:: Python
      :linenos:

      #! /usr/bin/env python

      import os
      import sys
      import pathlib

      import setuptools_scm
      import waves

      version = '0.1.0'

By convention, the `SCons`_ root project file is named ``SConstruct``. Because this is a `Python`_ file, we can import
`Python`_ libraries to help define project settings. The `shebang`_ in the first line is included to help text editors
identify the file as a Python file for syntax highlighting. Using the `PEP-8`_ formatting, the `Python`_ built-in
imports are listed in the first block and third-party imports are listed in the second block, including the `WAVES`_
package. Finally, the EABM version number is hardcoded into the project definition for these tutorials.

.. admonition:: SConstruct

   .. literalinclude:: ._SConstruct
      :language: Python
      :lineno-match:
      :end-before: marker-1
