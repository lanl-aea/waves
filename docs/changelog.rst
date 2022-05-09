.. _changelog:


#########
Changelog
#########

******************
0.1.5 (unreleased)
******************

New Features
============
- Add an Abaqus datacheck prior to solving the simulation target (:issue:`30`, :merge:`26`). By `Kyle Brindley`_.
- Limit the EABM default targets to the documentation. Requires simulation targets to be specified in the SCons command
  line arguments to avoid building all simulations from a bare ``scons`` execution (:issue:`32`, :merge:`27`). By `Kyle
  Brindley`_.

Bug fixes
=========
- Limit automatically appended target extensions for the AbaqusSolver builder to avoid inadvertent ``AlwaysBuild``
  behavior introduced by expected, but missing, file extensions that are never created (:issue:`41`, :merge:`28`). By
  `Kyle Brindley`_.

Enhancements
============
- Avoid build file creation in the source directory during copy/substitution operations, e.g. SolverPrep (:issue:`16`,
  :merge:`25`). By `Kyle Brindley`_.

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
- Use SCons-simulation repository version in SCons-EABM documentation (:issue:`31`, :merge:`18`). By `Kyle Brindley`_.

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
- Separate the Scons build system documentation from the associated SCons-EABM documentation (:issue:`26`, :merge:`16`).
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
