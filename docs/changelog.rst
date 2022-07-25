.. _changelog:


#########
Changelog
#########

*******************
0.2.2 (unreleased)
*******************

New Features
============
- Add the latin hypercube generator to the parameter study command line utility (:issue:`216`, :merge:`207`). By `Kyle
  Brindley`_.

Bug fixes
=========
- Fix the representation of strings in the parameter generator parameter set output files (:issue:`215`, :merge:`206`).
  By `Kyle Brindley`_.

Documentation
=============
- Provide Abaqus files in the appendix for users without access to the WAVES or WAVES-EABM repository files
  (:issue:`206`, :merge:`203`). By `Kyle Brindley`_.
- Remove the ABC ParameterGenerator abstract method docstrings from the parameter generators' APIs (:issue:`213`,
  :merge:`204`). By `Kyle Brindley`_.

******************
0.2.1 (2022-07-22)
******************

Breaking changes
================
- Reform the parameter study xarray object to make it more intuitive (:issue:`210`, :merge:`197`). By `Kyle Brindley`_.

New Features
============
- Add the ``find_program`` method to search for an ordered list of program names (:issue:`65`, :merge:`185`). By `Kyle
  Brindley`_.
- Add a LatinHypercube parameter generator (:issue:`77`, :merge:`192`). By `Kyle Brindley`_.

Internal Changes
================
- Remove unused ``pyyaml`` package from WAVES-EABM environment lists (:issue:`197`, :merge:`182`). By `Kyle Brindley`_.
- Use the ``find_program`` method to search for an ordered list of Abaqus executable names in the WAVES-EABM and
  tutorials. Prefer the install naming convention ``abqYYYY`` (:issue:`65`, :merge:`185`). By `Kyle Brindley`_.
- Move the parameter set name creation to a dedicated function shared by all parameter generator classes (:issue:`205`,
  :merge:`189`). By `Kyle Brindley`_.
- Placeholder Latin Hypercube parameter generator with functioning schema validation (:issue:`207`, :merge:`191`). By
  `Kyle Brindley`_.
- Add ``scipy`` to the waves development environment for the latin hypercube parameter generator (:issue:`208`,
  :merge:`193`). By `Kyle Brindley`_.
- Mock ``scipy`` in the Sphinx documentation build to reduce package build time requirements (:merge:`194`). By `Kyle
  Brindley`_.
- Add ``smt`` to waves development environment to support latin hypercube parameter generator (:merge:`195`). By `Kyle
  Brindley`_.

Documentation
=============
- Add minimal structure to data extraction tutorial (:issue:`198`, :merge:`183`). By `Kyle Brindley`_.
- Add a brief draft of the documentation computational practice discussion (:issue:`124`, :merge:`184`). By `Kyle
  Brindley`_.
- Add a Cubit example draft to the tutorials (:issue:`203`, :merge:`186`). By `Kyle Brindley`_.
- Separate the internal and external API (:issue:`200`, :merge:`188`). By `Kyle Brindley`_.
- Add private methods to the internal API (:merge:`190`). By `Kyle Brindley`_.
- Add a mulit-action task example using the general purpose SCons Command builder (:issue:`196`, :merge:`198`). By `Kyle
  Brindley`_.
- Add a Latin Hypercube tutorial (:issue:`211`, :merge:`200`). By `Kyle Brindley`_.

Enhancements
============
- Add support for ``odb_extract`` arguments in the ``abaqus_extract`` builder (:issue:`200`, :merge:`188`) By `Kyle
  Brindley`_.

*******************
0.1.17 (2022-07-18)
*******************

Documentation
=============
- Add the compute environment section to the computational practices discussion (:issue:`126`, :merge:`179`). By `Kyle
  Brindley`_.

*******************
0.1.16 (2022-07-14)
*******************

Internal Changes
================
- Reduce the simulation variables and substitution dictionary to a single dictionary (:issue:`181`, :merge:`177`). By
  `Kyle Brindley`_.

Documentation
=============
- Update Scons terminal output and sample tree output in the tutorials to reflect the state of a user's tutorial files
  (:issue:`189`, :merge:`174`). By `Thomas Roberts`_.
- Add a pure SCons quickstart tutorial (:issue:`48`, :merge:`173`). By `Kyle Brindley`_.

*******************
0.1.15 (2022-07-14)
*******************

Breaking changes
================
- Require at least one target for the AbaqusJournal and PythonScript builders (:issue:`188`, :merge:`166`). By `Kyle
  Brindley`_.
- Return parameter study as an xarray dataset instead of a text YAML dictionary. Necessary for future output type
  options and multi-index tables, e.g. Latin Hypercube value and quantile information (:issue:`70`, :merge:`170`). By
  `Kyle Brindley`_.
- Convert project command line variables to command line options (:issue:`179`, :merge:`169`). By `Kyle Brindley`_.

New Features
============
- Add ODB extract builder and EABM tutorial configuration (:issue:`92`, :merge:`100`). By `Prabhu Khalsa`_ and `Kyle
  Brindley`_.

Bug fixes
=========
- Fix the output and return code unpacking when calling the ``run_external`` function from ``odb_extract.main``
  (:issue:`92`, :merge:`100`). By `Kyle Brindley`_.
- Execute the ODB parser for H5 file output (:issue:`92`, :merge:`100`). By `Kyle Brindley`_.
- Fix the ``odb_extract`` entry point specification. New specification required by new internal interface introduced in
  :merge:`100` (:issue:`186`, :merge:`163`). By `Kyle Brindley`_.
- Fix a missing file copy required by the Conda recipe test definition (:issue:`187`, :merge:`164`). By `Kyle
  Brindley`_.
- Match the script builder redirected STDOUT file name to the first target. Required to allow multiple tasks that
  execute the same script. Adds new target list requirement the script builders (:issue:`188`, :merge:`166`). By `Kyle
  Brindley`_.

Documentation
=============
- Update project URLs to reflect the move to the AEA Gitlab group (:issue:`183`, :merge:`160`). By `Kyle Brindley`_.
- Add a missing input file to the SolverPrep tutorial instructions (:issue:`192`, :merge:`167`). By `Kyle Brindley`_.
- Clarify target list requirements and emitter behavior in the builder APIs (:issue:`188`, :merge:`160`). By `Kyle
  Brindley`_.
- Add a discussion about the types, purposes, and values of modsim repository testing (:issue:`127`, :merge:`171`). By
  `Kyle Brindley`_.
- Fix typos and typesetting issues in Tutorial 01: Geometry (:issue:`191`, :merge:`172`). By `Thomas Roberts`_.

Internal Changes
================
- Remove remnants of the parameter study file I/O that is no longer necessary from the cartesian product configuration
  (:issue:`184`, :merge:`161`).  By `Kyle Brindley`_.
- Remove the ``.jnl`` file from the list of targets appended by the Abaqus journal builder (:issue:`180`, :merge:`162`).
  By `Matthew Fister`_.
- Explicitly manage the ``.jnl`` target additions for more complete SCons clean operations (:issue:`185`, :merge:`168`).
  By `Kyle Brindley`_.

*******************
0.1.14 (2022-06-30)
*******************

Documentation
=============
- Complete WAVES Tutorial 06: Include Files (:issue:`102`, :merge:`151`). By `Thomas Roberts`_ and `Kyle Brindley`_.
- Completed WAVES Tutorial 02: Partition and Mesh (:issue:`98`, :merge:`149`). By `Thomas Roberts`_ and `Kyle
  Brindley`_.
- Completed WAVES Tutorial 05: Parameter Substitution (:issue:`137`, :merge:`101`). By `Thomas Roberts`_ and `Kyle
  Brindley`_.

*******************
0.1.13 (2022-06-29)
*******************

Bug fixes
=========
- Abaqus File Parser will now handle blank values for Integration Points even when the 'IP' heading is given (:issue:`176`, :merge:`153`). By `Prabhu Khalsa`_.

Documentation
=============
- Add source code links to WAVES and WAVES-EABM documentation (:issue:`173`, :merge:`148`). By `Kyle Brindley`_.

Internal Changes
================
- Move the argument parsing for partitioning and meshing to dedicated argument parser functions (:issue:`174`,
  :merge:`150`). By `Thomas Roberts`_.
- Remove the dummy file targets for documentation builds to allow conditional re-building only on source/target content
  changes (:issue:`5`, :merge:`154`). By `Kyle Brindley`_.
- Unpinned Sphinx version. Added fix to avoid warnings treated as errors (:issue:`178`, :merge:`155`).
  By `Sergio Cordova`_.

*******************
0.1.12 (2022-06-17)
*******************

Documentation
=============
- Move the build wrapper discussion and usage into the command line utilities section (:issue:`168`, :merge:`143`). By
  `Kyle Brindley`_.
- Add TOC tree captions as PDF parts in the PDF documentation build (:issue:`169`, :merge:`144`). By `Kyle Brindley`_.

Internal Changes
================
- Limit Gitlab-Pages build to the HTML documentation (:issue:`168`, :merge:`143`). By `Kyle Brindley`_.
- Fix the WAVES-EABM Gitlab-Pages documentation build (:issue:`170`, :merge:`145`). By `Kyle Brindley`_.

*******************
0.1.11 (2022-06-17)
*******************

New Features
============
- Add an SCons build wrapper to manage unique build directory names and Git clone operations (:issue:`114`,
  :merge:`141`). By `Kyle Brindley`_.

Documentation
=============
- Add brandmark logo to documentation (:issue:`133`, :merge:`128`). By `Kyle Brindley`_.
- Update the Abaqus solver builder's docstring action to match the implementation (:issue:`163`, :merge:`134`). By `Kyle
  Brindley`_.
- Update the developer documentation for WAVES repository testing and add a code snippet to help find the CI test
  targets (:issue:`160`, :merge:`135`). By `Kyle Brindley`_.
- Use copy and paste-able commands for SCons man page location and linking instructions (:issue:`164`, :merge:`136`). By
  `Kyle Brindley`_.
- Complete WAVES Tutorial 4: Simulation (:issue:`100`, :merge:`117`). By `Thomas Roberts`_.
- Add brandmark to WAVES-EABM documentation (:issue:`166`, :merge:`139`). By `Kyle Brindley`_.
- Add manpage and PDF builders for the WAVES documentation and bundle with the Conda package (:issue:`167`,
  :merge:`140`). By `Kyle Brindley`_.
- Update the Abaqus documentation links to use the Abaqus 2021 documentation (:issue:`165`, :merge:`138`). By `Thomas
  Roberts`_.

Internal Changes
================
- Added three new documentation aliases to match the sphinx-build builders: html, latexpdf, man. "documentation" alias
  now collects all three documentation build types (:issue:`167`, :merge:`140`). By `Kyle Brindley`_.

*******************
0.1.10 (2022-06-09)
*******************

Breaking changes
================
- Remove the ``abaqus_wrapper`` bash utility in favor of an SCons builder solution (:issue:`22`, :merge:`127`). By
  `Kyle Brindley`_.
- Use ``*.stdout`` extension for re-directed STDOUT and STDERR streams to avoid clobbering third-party software log
  files (:issue:`159`, :merge:`131`). By `Kyle Brindley`_.

Documentation
=============
- Add tutorial description page for summary instructions (:issue:`144`, :merge:`121`). By `Kyle Brindley`_.
- Add draft of the computational practices version control section (:issue:`123`, :merge:`122`). By `Kyle Brindley`_.

Internal Changes
================
- Clean at the end of a branch's Gitlab-Pages job to avoid incomplete clean operations when main/dev differ in their
  target file(s) (:issue:`152`, :merge:`125`). By `Kyle Brindley`_.
- Improve directory location change logic in the Gitlab-Pages job (:issue:`154`, :merge:`126`). By `Kyle Brindley`_.
- Keep the SConstruct markers to avoid unecessarily long and possibly confusing diffs in the tutorial documentation
  (:issue:`158`, :merge:`129`). By `Kyle Brindley`_.

Enhancements
============
- Treat the EABM source files like a local package for re-using project settings (:issue:`150`, :merge:`124`). By `Kyle
  Brindley`_.

******************
0.1.9 (2022-06-03)
******************

Documentation
=============
- Add minimum scaffolding for the solverprep tutorial documentation (:issue:`145`, :merge:`111`). By `Kyle
  Brindley`_.
- Add minimum scaffolding for the simulation tutorial documentation (:issue:`146`, :merge:`112`). By `Kyle
  Brindley`_.
- Add a quickstart tutorial using a single project definition file (:issue:`147`, :merge:`113`). By `Kyle Brindley`_.
- Add the EABM API and CLI to an Appendices section in the WAVES documentation (:issue:`138`, :merge:`104`).
  By `Thomas Roberts`_.
- Revise Tutorial 01: Geometry to match formatting of other tutorials (:issue:`148`, :merge:`116`). By
  `Thomas Roberts`_.
- Completed WAVES Tutorial 03: SolverPrep (:issue:`99`, :merge:`115`). By `Thomas Roberts`_.

******************
0.1.8 (2022-06-02)
******************

New Features
============
- Add the command line tools odb_extract, msg_parse, and sta_parse (:issue:`93`, :merge:`88`). By `Prabhu Khalsa`_.

Bug fixes
=========
- Workaround the self-signed re-git.lanl.gov ssl certificates (:issue:`142`, :merge:`109`). By `Kyle Brindley`_.

Documentation
=============
- Update the SConstruct example for the Python script builder (:issue:`113`, :merge:`83`). By `Kyle Brindley`_.
- Fix the out-of-order build/test/documentation examples as bulleted lists instead of enumerated lists (:issue:`115`,
  :merge:`84`). By `Kyle Brindley`_.
- Draft outline for the computational tools and practices "theory" manual (:issue:`96`, :merge:`85`). By `Kyle
  Brindley`_.
- Add the project configuration (SConstruct) tutorial (:issue:`119`, :merge:`89`). By `Kyle Brindley`_.
- Add minimum scaffolding for the parameter substitution tutorial documentation (:issue:`137`, :merge:`101`). By `Kyle
  Brindley`_.
- Draft of Tutorial 1: Geometry (:issue:`45`, :merge:`35`). By `Thomas Roberts`_.
- Completed WAVES Tutorial 1: Geometry (:issue:`129`, :merge:`94`). By `Thomas Roberts`_.
- Add minimum scaffolding for the include files tutorial documentation (:issue:`139`, :merge:`105`). By `Kyle
  Brindley`_.
- Add minimum scaffolding for the cartesian product tutorial documentation (:issue:`140`, :merge:`106`). By `Kyle
  Brindley`_.

Internal Changes
================
- Create a list of files to be copied to the documentation build directory for include statements in ``.rst`` files
  (:issue:`120`, :merge:`90`). By `Thomas Roberts`_.
- Specify Sphinx v4.5.0 in the enviroment file (:issue:`121`, :merge:`91`). By `Thomas Roberts`_.
- Removed duplicate code in the docs/SConscript file (:issue:`128`, :merge:`93`). By `Sergio Cordova`_
- Changed test_builders so journal.stdout is not created by two targets (:issue:`130`, :merge:`95`). By `Prabhu Khalsa`_
- Create per-tutorial EABM stub project definition files (SConstruct) to aid in incremental changes in the tutorial
  documentation and allow for per-tutorial regression tests (:issue:`131`, :merge:`97`). By `Kyle Brindley`_.
- Added odb_extract rst documentation and added odb_extract, msg_parse, and sta_parse to pyrpojects.toml
  (:issue:`132`, :merge:`96`). By `Prabhu Khalsa`_
- Added StaFileParser API documentation (:issue:`135`, :merge:`99`). By `Prabhu Khalsa`_
- Added MsgFileParser API documentation (:issue:`136`, :merge:`98`). By `Prabhu Khalsa`_

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
