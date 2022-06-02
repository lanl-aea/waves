.. _changelog:


#########
Changelog
#########

******************
0.1.8 (unreleased)
******************

New Features
============
- Add the command line tools odb_extract, msg_parse, and sta_parse (:issue:`93`, :merge:`88`). By `Prabhu Khalsa`_.

Documentation
=============
- Update the SConstruct example for the Python script builder (:issue:`113`, :merge:`83`). By `Kyle Brindley`_.
- Fix the out-of-order build/test/documentation examples as bulleted lists instead of enumerated lists (:issue:`115`,
  :merge:`84`). By `Kyle Brindley`_.
- Draft outline for the computational tools and practices "theory" manual (:issue:`96`, :merge:`85`). By `Kyle
  Brindley`_.

Internal Changes
================
- Create a list of files to be copied to the documentation build directory for include statements in ``.rst`` files
  (:issue:`120`, :merge:`90`). By `Thomas Roberts`_.
- Specify Sphinx v4.5.0 in the enviroment file (:issue:`121`, :merge:`91`). By `Thomas Roberts`_.
- Removed duplicate code in the docs/SConscript file (:issue:`128`, :merge:`93`). By `Sergio Cordova`_
- Changed test_builders so journal.log is not created by two targets (:issue:`130`, :merge:`95`). By `Prabhu Khalsa`_
- Create per-tutorial EABM stub project definition files (SConstruct) to aid in incremental changes in the tutorial
  documentation and allow for per-tutorial regression tests (:issue:`131`, :merge:`97`). By `Kyle Brindley`_.

******************
0.1.7 (2022-05-27)
******************

Breaking changes
================
- Re-arrange the EABM stub source files to allow identically named Abaqus and Cubit journal files when those files
  perform a nominally identical task (:issue:`109`, :merge:`77`). By `Kyle Brindley`_.

New Features
============
- Add the SCons target definition equivalent to the ECMF and CMake-simulation cartesian product parameterized simulation
  files (:issue:`61`, :merge:`64`). By `Kyle Brindley`_.
- Record the Abaqus environment for each Abaqus builder task (:issue:`85`, :merge:`75`). By `Kyle Brindley`_.
- Add prototype Cubit geometry tutorial source files (:issue:`108`, :merge:`76`). By `Kyle Brindley`_.
- Add Cubit partition and mesh tutorial source files (:issue:`110`, :merge:`78`). By `Kyle Brindley`_.
- Add a Cubit journal files to Abaqus solver tutorial source files (:issue:`111`, :merge:`79`). By `Kyle Brindley`_.

Documentation
=============
- Update the build discussion to include references to the SCons complete CLI options. Add missing portions of the WAVES
  development operations documentation (:issue:`49`, :merge:`69`). By `Kyle Brindley`_.
- Typesetting update for mesh node and element set names in the meshing journal file API (:issue:`84`, :merge:`71`). By
  `Kyle Brindley`_.
- Add the Python package dependency list to the HTML documentation (:issue:`81`, :merge:`72`). By `Kyle Brindley`_.
- Update the EABM stub environment activation and creation instructions (:issue:`82`, :merge:`73`). By `Kyle Brindley`_.
- Update the tutorial Abaqus journal files CLI documentation for consistency with the API (:issue:`83`, :merge:`74`). By
  `Kyle Brindley`_.

Internal Changes
================
- Collect target list with a Python built-in list for consistency across SConscript solutions with the paramerization
  solution (:issue:`89`, :merge:`65`). By `Kyle Brindley`_.
- Make the Abaqus and documentation builders thread safe for SCons parallel threading feature, ``--jobs`` option
  (:issue:`62`, :merge:`66`). By `Kyle Brindley`_.
- Update the parameter study for more useful post-processing demonstrations (:issue:`107`, :merge:`70`). By `Kyle
  Brindley`_.
- Separate the EABM specific abaqus utility function from the meshing journal file (:issue:`53`, :merge:`80`). By `Kyle
  Brindley`_.

Enhancements
============
- Use the parameter study object directly to avoid unnecessary EABM parameter study file I/O (:issue:`91`, :merge:`67`).
  By `Kyle Brindley`_.

******************
0.1.6 (2022-05-17)
******************

Breaking changes
================
- Output parameter set files in YAML syntax instead of CMake syntax (:issue:`71`, :merge:`59`). By `Kyle Brindley`_.
- Avoid writing parameter study meta file by default. Never write parameter meta file for output to STDOUT (:issue:`87`,
  :merge:`61`). By `Kyle Brindley`_.
- Change the project name to "WAVES" and update the Git repository URL and documentation (:issue:`88`, :merge:`62`). By
  `Kyle Brindley`_.

New Features
============
- Re-work the parameter generators for direct use in an SCons builder: validate schema on instantiation, provide
  argument defaults on instantiation, output list of pathlib.Path file objects that will be written (:issue:`60`,
  :merge:`60`). By `Kyle Brindley`_.

Documentation
=============
- Add the root project name back to the documentation build (:issue:`86`, :merge:`57`). By `Kyle Brindley`_.

Internal Changes
================
- Exclude documentation source files and build artifacts from the Conda package (:issue:`68`, :merge:`54`). By `Kyle
  Brindley`_.
- Move Conda package constants into a package internal settings file. Remove as many project settings from SCons
  configuration files as possible (:issue:`64`, :merge:`55`). By `Kyle Brindley`_.
- Separate the parametery study utility from the parameter generators module (:issue:`64`, :merge:`55`).  By `Kyle
  Brindley`_.
- Handle parameter study utility missing positional arguments gracefully by printing usage (:issue:`64`, :merge:`55`).
  By `Kyle Brindley`_.

******************
0.1.5 (2022-05-12)
******************

New Features
============
- Add an Abaqus datacheck prior to solving the simulation target (:issue:`30`, :merge:`26`). By `Kyle Brindley`_.
- Limit the EABM default targets to the documentation. Requires simulation targets to be specified in the SCons command
  line arguments to avoid building all simulations from a bare ``scons`` execution (:issue:`32`, :merge:`27`). By `Kyle
  Brindley`_.
- Make the variant (build) directory a command line variable option (:issue:`25`, :merge:`29`). By `Kyle Brindley`_.
- Build the project internal variables into a substitution dictionary that can be passed to SConscript files
  (:issue:`13`, :merge:`30`). By `Kyle Brindley`_.
- Add a copy and substitute target builder to WAVES (:issue:`28`, :merge:`32`). By `Kyle Brindley`_.
- Add an alias collector solution to provide a list of available aliases in the project help message (:issue:`33`,
  :merge:`38`). By `Kyle Brindley`_.
- Add the SCons target definition equivalent to the ECMF and CMake-simulation parameter substitution tutorial files (:issue:`57`,
  :merge:`43`). By `Kyle Brindley`_.
- Add the SCons target definition equivalent to the ECMF include file tutorial (:issue:`59`, :merge:`44`). By `Kyle
  Brindley`_.
- Conditionally ignore Sphinx targets when the sphinx-build is not found in the construction environment (:issue:`3`,
  :merge:`45`). By `Kyle Brindley`_.
- Provide and use an override variable to the conditional ignore behavior. Useful for requiring all targets in a build,
  particularly for CI testing (:issue:`3`, :merge:`45`). By `Kyle Brindley`_.
- Conditionally skip simulation target trees when a required program is missing (:issue:`38`, :merge:`46`). By `Kyle
  Brindley`_.

Bug fixes
=========
- Limit automatically appended target extensions for the AbaqusSolver builder to avoid inadvertent ``AlwaysBuild``
  behavior introduced by expected, but missing, file extensions that are never created (:issue:`41`, :merge:`28`). By
  `Kyle Brindley`_.

Documentation
=============
- Link from the AbaqusSolver builder to the Abaqus wrapper shell script to help explain the action definition
  (:issue:`42`, :merge:`31`). By `Kyle Brindley`_.
- Add a command line interface (CLI) documentation page (:issue:`44`, :merge:`34`). By `Thomas Roberts`_.
- Fix WAVES builder docstring example syntax (:issue:`54`, :merge:`36`). By `Kyle Brindley`_.
- Create a custom usage message for the geometry argument parser that displays the proper command for running an Abaqus
  journal file (:issue:`55`, :merge:`37`). By `Thomas Roberts`_.

Internal Changes
================
- Move the geometry argument parser to a stand-alone function within the geometry script (:issue:`43`, :merge:`33`). By
  `Thomas Roberts`_.
- Unit test the WAVES copy and substitute builder function (:issue:`52`, :merge:`40`). By `Kyle Brindley`_.
- Unit test the WAVES Abaqus Journal builder and emitter (:issue:`50`, :merge:`41`). By `Kyle Brindley`_.
- Unit test the WAVES Abaqus Solver builder and emitter (:issue:`51`, :merge:`51`). By `Kyle Brindley`_.
- Search a user provided construction environment for the 'abaqus_wrapper' program before using the WAVES internal
  project bin. Allows users to override the WAVES Abaqus wrapper with their own (:issue:`40`, :merge:`47`). By `Kyle Brindley`_.
- Separate the development environment fast tests from the Conda build/test job. Skip the WAVES documentation build in the
  Conda packaging process (:issue:`67`, :merge:`48`). By `Kyle Brindley`_.
- Deploy as a ``noarch`` Conda package (:issue:`69`, :merge:`51`). By `Kyle Brindley`_.

Enhancements
============
- Avoid build file creation in the source directory during copy/substitution operations, e.g. SolverPrep (:issue:`16`,
  :merge:`25`). By `Kyle Brindley`_.
- Provide an optional Abaqus program argument to the Abaqus builders (:issue:`40`, :merge:`47`). By `Kyle Brindley`_.

******************
0.1.4 (2022-05-06)
******************

New Features
============
- Add parameter study module and tests (:issue:`27`, :merge:`19`). By `Kyle Brindley`_.
- Add Conda build recipe (:issue:`35`, :merge:`21`). By `Kyle Brindley`_.
- Deploy Conda package as "waves" to AEA Conda channel (:issue:`36`, :merge:`22`). By `Kyle Brindley`_.

Documentation
=============
- Use WAVES repository version in WAVES-EABM documentation (:issue:`31`, :merge:`18`). By `Kyle Brindley`_.

******************
0.1.3 (2022-05-05)
******************

New Features
============
- Append the Abaqus journal Builder managed targets automatically (:issue:`18`, :merge:`10`). By `Kyle Brindley`_.
- Separate the common custom builders from the EABM SCons project definition (:issue:`19`, :merge:`11`). By `Kyle
  Brindley`_.
- Add a variable to pass through additional Abaqus command line arguments to the Abaqus journal file builder
  (:issue:`19`, :merge:`11`). By `Kyle Brindley`_.
- Add the SCons target definition equivalent to the ECMF and CMake-simulation Abaqus simulation execution (:issue:`21`,
  :merge:`13`). By `Kyle Brindley`_.

Bug fixes
=========
- Avoid modifying the contents or timestamp of input files in Abaqus journal files (:issue:`17`, :merge:`12`). By `Kyle
  Brindley`_.

Documentation
=============
- Add SCons custom builder documentation for the build system (:issue:`19`, :merge:`11`). By `Kyle Brindley`_.
- Separate the Scons build system documentation from the associated WAVES-EABM documentation (:issue:`26`, :merge:`16`).
  By `Kyle Brindley`_.

Internal Changes
================
- Remove the dummy ``{job_name}.touch`` file from the Abaqus wrapper. SCons does not automatically delete target file(s)
  when the build fails like GNU Make or CMake does (:issue:`24`, :merge:`14`). By `Kyle Brindley`_.

******************
0.1.2 (2022-05-04)
******************

New Features
============
- Add the SCons target definition equivalent to the ECMF and CMake-simulation "Tutorial 01: geometry" (:issue:`10`,
  :merge:`3`). By `Kyle Brindley`_.
- Add the SCons target definition equivalent to the ECMF and CMake-simulation "Tutorial 02: partition and mesh"
  (:issue:`11`, :merge:`4`). By `Kyle Brindley`_.
- Add the SCons target definition equivalent to the ECMF and CMake-simulation "Tutorial 03: solverprep" (:issue:`14`,
  :merge:`6`). By `Kyle Brindley`_.
- Link the SCons man pages to the expected man page directory of the Conda environment (:issue:`15`, :merge:`7`). By
  `Kyle Brindley`_.

Bug fixes
=========
- Fix the documentation alias declaration (:issue:`6`, :merge:`8`). By `Kyle Brindley`_.

Documentation
=============
- Add Abaqus journal file API to documentation (:issue:`12`, :merge:`5`). By `Kyle Brindley`_.

******************
0.1.1 (2022-05-03)
******************

New Features
============
- Functioning Gitlab-CI environment creation job. By `Kyle Brindley`_.
- Functioning documentation target build and Gitlab-Pages CI job. By `Kyle Brindley`_.
- Automatic micro version number bumping for dev->main merges (:issue:`1`, :merge:`1`). By `Kyle Brindley`_.
- Retrieve project version number from Git tags for the SCons environment (:issue:`1`, :merge:`1`). By `Kyle Brindley`_.

******************
0.1.0 (2022-04-20)
******************

Breaking changes
================

New Features
============

Bug fixes
=========

Documentation
=============

Internal Changes
================

Enhancements
============
