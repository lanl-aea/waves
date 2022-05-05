.. _changelog:


#########
Changelog
#########

******************
0.1.3 (unreleased)
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
