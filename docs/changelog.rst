.. _changelog:

#########
Changelog
#########

*******************
0.13.6 (unreleased)
*******************

*******************
0.13.5 (2025-06-05)
*******************

New Features
============
- Experimental Quantity of Intereset (QOI) module for advanced post-processing and regression testing (:issue:`904`,
  :merge:`1164`). By `Matthew Fister`_ and `Kyle Brindley`_.

Internal Changes
================
- Skip ``twine check`` test on macOS until shell kill error is fixed. By `Kyle Brindley`_.
- Restructure internal deployment around Gitlab-CI tag pipelines. By `Kyle Brindley`_.
- Preserve QOI datatree structure when merging (:merge:`1205`). By `Matthew Fister`_.
- Allow a QOI date attribute to be specified via the ``archive`` subcommand (:merge:`1211`). By `Matthew Fister`_.
- Only propagate common attributes when merging QOI xarray objects. (:merge:`1206`). By `Matthew Fister`_.
- Create helper function for generating multiple kinds of PDF reports (:merge:`1212`). By `Matthew Fister`_.
- Fully replace cached CI environments with a CI job-specific environment to reduce collisions in Conda operations that
  cause false negatives. By `Kyle Brindley`_.

*******************
0.13.4 (2025-05-29)
*******************

Internal Changes
================
- Fix PyPI deployments (:merge:`1200`). By `Kyle Brindley`_.

*******************
0.13.3 (2025-05-29)
*******************

Internal Changes
================
- Fix GitHub Actions deployments (:merge:`1199`). By `Kyle Brindley`_.

*******************
0.13.2 (2025-05-29)
*******************

Documentation
=============
- Add `Chris Johnson`_ to authors list (:issue:`906`, :merge:`1181`). By `Chris Johnson`_.
- Replace GNU Make lesson plan reference with SCons lesson plan (:issue:`913`, :merge:`1183`). By `Kyle Brindley`_.
- Handle time increments in Gmsh+Calculix tutorial (:issue:`915`, :merge:`1187`). By `Kyle Brindley`_.
- Update copyright year range. By `Kyle Brindley`_.
- Remove Gmsh+CacluliX tee behavior because it results in false positives during workflow execution (:issue:`912`,
  :merge:`1190`). By `Kyle Brindley`_.
- Rewrite the Gmsh+Calculix tutorial as a fully open-source workflow equivalent to the existing quickstart with Abaqus
  (:merge:`1191`). By `Kyle Brindley`_.
- Build documentation with full runtime dependencies for resolved type hints (:merge:`1195`). By `Kyle Brindley`_.
- Minor updates to the pure SCons quickstart for better use of executable program path environment variable. By `Kyle
  Brindley`_.

Internal Changes
================
- Begin generalizing internal parameter study merge operations for a future merge arbitrary number of studies feature
  (:issue:`841`, :merge:`1184`). By `Chris Johnson`_.
- System test for printing available fetch files. By `Kyle Brindley`_.
- Gitlab-CI job specific environment for HPC CI job. By `Kyle Brindley`_.
- Skip fragile modsim template documentation build system tests with regular, intermittent failures (:merge:`1192`). By
  `Kyle Brindley`_.
- Add an option to keep the system test build artifacts for troubleshooting (:merge:`1194`). By `Kyle Brindley`_.
- Add more minimal CI job environments to reduce collisions in cached environment jobs (:merge:`1195`). By `Kyle
  Brindley`_.

*******************
0.13.1 (2025-04-16)
*******************

Bug fixes
=========
- Fix the GitHub-Actions Conda environment creation options. By `Kyle Brindley`_.

*******************
0.13.0 (2025-04-14)
*******************

Bug fixes
=========
- Remove type casting for combinations of ints/floats, ints/bools, and floats/bools during parameter study merge
  operations. Add unit tests for set hash calculation and system tests for read from disk operations to catch more type
  casting errors (:issue:`907`, :merge:`1173`). By `Kyle Brindley`_.

Breaking changes
================
- Remove the parameter generator ``scons_write`` action from the public API in favor of the full
  ``parameter_study_write`` pseudo-builder (:issue:`883`, :merge:`1167`). By `Kyle Brindley`_.
- Remove the parameter generator class dry run API option in favor of the write method API (:issue:`859`,
  :merge:`1166`). By `Kyle Brindley`_.
- Deprecate old naming convention for project help messages in favor of ``project_help_`` naming convention
  (:issue:`862`, :merge:`1168`). By `Kyle Brindley`_.
- Remove deprecated set and hash coordinate keys (:issue:`855`, :merge:`1169`). By `Kyle Brindley`_.
- Remove duplicate Abaqus option handling and convert to flag style options in AbaqusPseudoBuilder (:issue:`867`,
  :merge:`1170`). By `Kyle Brindley`_.

********************
0.12.10 (2025-04-10)
********************

Documentation
=============
- Avoid module conflicts with common AEA modulefiles in the Quinoa tutorial (:issue:`902`, :merge:`1162`). By `Kyle
  Brindley`_.

Internal Changes
================
- Explicitly limit VTK version that crashes on macOS (:issue:`899`, :merge:`1161`). By `Kyle Brindley`_.
- Overhaul CI environment handling to reduce collisions in Conda operations and simplify CI job cleanup (:merge:`1163`).
  By `Kyle Brindley`_.

Enhancements
============
- Print shell command STDERR message on exceptions when using the construction shell environment method (:issue:`902`,
  :merge:`1162`). By `Kyle Brindley`_.

*******************
0.12.9 (2025-04-03)
*******************

New Features
============
- Experimental builder support for Truchas (:issue:`890`, :merge:`1140`). By `Kyle Brindley`_.

Bug fixes
=========
- Include the README and pyproject.toml configuration in the Gitlab-Registry PyPI style pip package (:merge:`1146`,
  :merge:`1148`). By `Kyle Brindley`_.

Documentation
=============
- Add external resource documentation to modsim templates (:issue:`846`, :merge:`1139`). By  `Chris Johnson`_.
- Match work-in-progress Truchas tutorial source files more closely to the WAVES quickstart tutorial. Files may be
  fetched with ``waves fetch tutorials/tutorial_truchas`` (:merge:`1145`). By `Kyle Brindley`_.
- Add Spack to installation instructions and compute environment management discussion (:issue:`894`, :merge:`1157`). By
  `Kyle Brindley`_.

Internal Changes
================
- Set minimum SALib version to match introduction of ``sample.sobol`` module (:merge:`1147`). By `Kyle Brindley`_.
- Add command line interface for greater package recipe support to documentation packaging post-pip-install utility
  (:issue:`896`, :merge:`1149`). By `Kyle Brindley`_.
- Create build and install aliases to make packaging operations more consistent across multiple package managers: pip,
  conda, spack (:issue:`893`, :merge:`1150`). By `Kyle Brindley`_.
- Re-organize GitHub Actions around a conda-build test workflow and a release workflow. Include automated PyPI
  publication in the release workflow and remove the conda package from the release artifacts (:issue:`897`,
  :merge:`1155`). By `Kyle Brindley`_.
- Add a CI job for testing the as-installed pip package in a Python venv (:issue:`898`, :merge:`1156`). By `Kyle
  Brindley`_.
- Add SCons, Sphinx, and CLI markers for pytest control while system testing (:issue:`900`, :merge:`1158`). By `Kyle
  Brindley`_.

*******************
0.12.8 (2025-03-18)
*******************

New Features
============
- Add one-at-a-time parameter generator. (:issue:`853`, :merge:`1101`). By  `Chris Johnson`_.
- Add public emitter factory for the Abaqus solver builder factory (:issue:`877`, :merge:`1120`). By `Kyle Brindley`_.
- Add public emitters for the Abaqus solver builder factory based builders (:issue:`877`, :merge:`1120`). By `Kyle
  Brindley`_.
- Add Abaqus datacheck, explicit, and standard builders with emitters to the WAVES construction environment
  (:issue:`877`, :merge:`1120`). By `Kyle Brindley`_.

Bug fixes
=========
- Allow periods in Abaqus pseudo-builder job names (:issue:`878`, :merge:`1119`). By `Kyle Brindley`_.
- Handle the project help keyword argument breaking change from ``keep_local`` to ``local_only`` released as a fix in
  SCons 4.9.0: https://scons.org/scons-490-is-available.html. The ``project_help`` related functions make the same
  breaking change in the keyword argument name to match SCons, but preserve support for older versions of SCons by
  falling back to the older keyword argument when necessary (:issue:`879`, :merge:`1128`). By `Kyle Brindley`_.
- Avoid always re-build behavior in parameter study write pseudo-builder (:issue:`881`, :merge:`1131`). By `Kyle
  Brindley`_.
- Use the required ``job`` option of the Abaqus solver builder factory in the Abaqus pseudo-builder (:issue:`884`,
  :merge:`1133`). By `Kyle Brindley`_.

Documentation
=============
- Add completed parameter lists, returns, and typing hints to parameter generator private functions
  (:issue:`882`, :merge:`1134`). By  `Chris Johnson`_.
- Use the WAVES construction environment Abaqus solve builder factory in the tutorials (:issue:`876`, :merge:`1118`). By
  `Kyle Brindley`_.
- Explicit source and target lists in the tutorials to limit use of intermediate and advanced Python concepts. Users
  report that the mix of Python and SCons concepts makes learning SCons more difficult (:issue:`876`, :merge:`1118`).
  By `Kyle Brindley`_.
- Use Abaqus datacheck, explicit, and standard builders with emitters from the WAVES construction environment in modsim
  templates (:issue:`877`, :merge:`1120`). By `Kyle Brindley`_.
- Clarify all output files from tutorials' rectangle Abaqus journal files (:issue:`877`, :merge:`1120`). By `Kyle
  Brindley`_.
- Update the WAVES quickstart Abaqus installation note to take advantage of the ``--abaqus-command`` project command
  line option (:merge:`1126`). By `Kyle Brindley`_.
- Update tutorial visualize images (:issue:`835`, :merge:`1136`). By `Sergio Cordova`_.

Internal Changes
================
- Limit scope of changes possible in automated Gitlab release job (:issue:`875`, :merge:`1117`). By `Kyle Brindley`_.
- Remove the WAVES package mocks in the modsim template documentation configuration (:issue:`854`, :merge:`1125`). By
  `Kyle Brindley`_.
- Consistent naming convention for mock warning objects in ``tests_help_messages`` (:issue:`880`, :merge:`1130`). By
  `Chris Johnson`_.
- Remove Paraview from CI environment in favor of the fully specified runtime dependencies in ``ccx2paraview>=3.2.0``
  conda-forge package, which uses the mutually incompatible VTK package instead of Paraview. Make the Gmsh+CalculiX
  tutorial compatible with ``ccx2paraview>=3.1`` (:merge:`1132`). By `Kyle Brindley`_.
- Update visualize subcommand to use ``networkx.topological_generation`` to set image columns (:issue:`835`,
  :merge:`1129`). By `Sergio Cordova`_.

Enhancements
============
- Coerce each parameter into a consistent data type when initializing a parameter study. Warn the user when a parameter
  contains inconsistent data types. (:issue:`871`, :merge:`1123`). By `Chris Johnson`_.
- Added ``--break-paths`` option to visualize subcommand to format paths by inserting newlines after path separator
  (:issue:`887`, :merge:`1135`). By `Sergio Cordova`_.
- Improved edge rendering order to enhance node visibility in visualize subcommand output (:issue:`888`, :merge:`1137`).
  By `Sergio Cordova`_.

*******************
0.12.7 (2025-02-26)
*******************

Bug fixes
=========
- Add the Abaqus required ``-job`` option to the Abaqus solver builder factory (:issue:`868`, :merge:`1113`). By `Kyle
  Brindley`_.
- Fix ambiguous odb extract options when provided user odbreport arguments (:issue:`869`, :merge:`114`). By `Kyle
  Brindley`_.

Internal Changes
================
- Automated Gitlab release creation (:issue:`873`, :merge:`1116`). By `Kyle Brindley`_.

Enhancements
============
- Handle subdirectory style builds in the Abaqus Pseudo-Builder (:merge:`1111`). By `Kyle Brindley`_.
- Add Abaqus Pseudo-Builder to the WAVES construction environment (:merge:`1112`). By `Kyle Brindley`_.
- Reduce user argument caveats in odbreport options when using odb extract (:issue:`869`, :merge:`114`). By `Kyle
  Brindley`_.

*******************
0.12.6 (2025-02-24)
*******************

New Features
============
- Release the parameter study task/SConscript wrapper pseudo-builders as fully supported features (:merge:`1095`). By
  `Kyle Brindley`_.
- Add a project alias method and enhance the project help message to include descriptions for targets and aliases.
  (:issue:`838`, :merge:`1076`). By `Sergio Cordova`_.
- Experimental parameter study write pseudo-builders (:issue:`857`, :merge:`1097`). By `Kyle Brindley`_.

Documentation
=============
- Use hardcoded target and source filename strings in tutorials where possible. Users report that the mix of Python and
  SCons concepts makes learning SCons more difficult. Hardcoded filenames will make the task definitions easier to
  understand (:merge:`1107`, :merge:`1108`, :merge:`1109`). By `Kyle Brindley`_.

Internal Changes
================
- Replace optional mutable default arguments with None types (:issue:`850`, :merge:`1084`). By `Chris Johnson`_ and
  `Kyle Brindley`_.
- Flesh out unit tests related to output type file handling in parameter generator write method (:issue:`860`,
  :merge:`1098`). By `Kyle Brindley`_.
- Move the parameter study dry run implementation from the ParameterGenerator class initialization to the write method
  API. Maintain backward compatibility with a warning (:issue:`863`, :merge:`1099`). By `Kyle Brindley`_.
- Pin Fierro dependency while waiting on upstream package fix (:issue:`864`, :merge:`1102`). By `Kyle Brindley`_.
- Miscellaneous unit test coverage updates (:merge:`1103`, :merge:`1104`, :merge:`1106`). By `Kyle Brindley`_.
- Re-name project help functions for a more consistent naming scheme (:issue:`861`, :merge:`1100`).
  By `Sergio Cordova`_.

*******************
0.12.5 (2025-01-27)
*******************

Bug fixes
=========
- Fix integer type handling when merging parameter studies. Xarray merge type casts to float for comparisons during
  merge operations. Cast all data back to original types after merging parameter studies (:issue:`856`, :merge:`1088`).
  By `Kyle Brindley`_.

Internal Changes
================
- Match the Conda build recipes more closely to the conda-forge waves-feedstock for easier downstream/upstream diffs
  (:merge:`1078`). By `Kyle Brindley`_.
- Re-name the set coordinate name of parameter study Xarray Datasets from ``parameter_sets`` to ``set_name`` for better
  consistency across the internal naming convention, external API, and tutorial examples. Preserves the older coordinate
  with a user deprecation warning for the transition period and provides a new
  ``waves.parameter_generatores.SET_COORDINATE_KEY`` constant to help users to minimize hardcoded key names in the
  future (:merge:`1085`, :merge:`1086`). By `Kyle Brindley`_.
- Remove proxyout from the HPC configuration (:issue:`849`, :merge:`1083`). By `Chris Johnson`_.
- Updated tags for powershell runner (:issue:`858`, :merge:`1091`). By `Sergio Cordova`_.

Enhancements
============
- Perform more complete argument substitutions in the task parameter study pseudo-builder (:issue:`852`, :merge:`1080`).
  By `Kyle Brindley`_.
- Limit package mocks to those strictly necessary in modsim template documentation builds. Should minimize documentation
  build errors when users expand package requirements (:issue:`847`, :merge:`1082`). By `Kyle Brindley`_.

*******************
0.12.4 (2025-01-08)
*******************

Bug fixes
=========
- Add missing CalculiX command variable to WAVES construction environment (:issue:`842`, :merge:`1072`). By `Kyle
  Brindley`_.

Documentation
=============
- Fix grammatical errors and add clarifying language to tutorial 00 (:issue:`828`, :merge:`1047`). By `Prabhu Khalsa`_.
- Fix grammatical errors and add clarifying language to tutorial 01 (:issue:`829`, :merge:`1049`). By `Prabhu Khalsa`_.
- Fix grammatical errors and add clarifying language to tutorial 02 (:issue:`830`, :merge:`1052`). By `Prabhu Khalsa`_.
- Fix grammatical errors and add clarifying language to tutorial 03 (:issue:`831`, :merge:`1056`). By `Prabhu Khalsa`_.
- Add clarifying language to quickstart tutorial (:issue:`832`, :merge:`1057`). By `Prabhu Khalsa`_.
- Fix grammatical errors and add clarifying language to tutorial 04 (:issue:`833`, :merge:`1059`). By `Prabhu Khalsa`_.
- Add MPI and Charm++ references (:issue:`679`, :merge:`1044`). By `Kyle Brindley`_.

Internal Changes
================
- Use Abaqus 2024 in tutorials and system tests (:issue:`826`, :merge:`1040`). By `Kyle Brindley`_.
- More inclusive black autoformatting configuration (:merge:`1045`). By `Kyle Brindley`_.
- Persistent system test directories for failed tests (:issue:`827`, :merge:`1050`). By `Kyle Brindley`_.
- Enable Windows system tests for the ParameterStudySConcript feature (:issue:`802`, :merge:`1051`). By `Kyle
  Brindley`_.
- Enable Windows system test for the writing builders tutorial (:issue:`803`, :merge:`1054`). By `Kyle Brindley`_.
- Enable Windows system test for visualize subcommand (:issue:`796`, :merge:`1055`). By `Kyle Brindley`_.
- More robust modulefile decision in Quinoa tutorial (:issue:`836`, :merge:`1062`). By `Kyle Brindley`_.
- Enable pass-through testing of specific Abaqus and Cubit executable paths. Test at least one older version of each
  during scheduled regression CI pipelines (:merge:`1063`). By `Kyle Brindley`_.
- Test the external conda recipe on MacOS during normal CI pipelines (:issue:`801`, :merge:`1067`). By `Kyle Brindley`_.
- Test the external conda recipe on Windows during normal CI pipelines (:issue:`797`, :merge:`1068`). By `Kyle Brindley`_.
- Remove the incompatible Python 3.13, SCons 4.6 environment in the matrixed recipe build test (:issue:`840`,
  :merge:`1071`). By `Kyle Brindley`_.
- Skip Sierra system tests when using incompatible Python version 3.13 or newer (:issue:`843`, :merge:`1073`,
  :merge:`1074`). By `Kyle Brindley`_.

Enhancements
============
- Enable single directory, prefixed targets in the per-task parameter study pseudo-builder (:issue:`682`,
  :merge:`1046`). By `Kyle Brindley`_.
- Enable project-specific command line configuration controls when creating workflow visualizations with the visualize
  subcommand (:issue:`837`, :merge:`1065`). By `Kyle Brindley`_.

*******************
0.12.3 (2024-12-02)
*******************

Bug fixes
=========
- Use Abaqus solver builder factory in Abaqus Pseudo-builder docstring example (:merge:`1033`). By `Matthew Fister`_.

Documentation
=============
- Move the pure SCons quickstart tutorial to the supplemental lessons (:issue:`824`, :merge:`1027`). By `Kyle
  Brindley`_.

Internal Changes
================
- Add coverage to internal API unit tests (:merge:`1025`). By `Kyle Brindley`_.
- Strong style enforcement and wholesale updates to all Python 2/3 files with the black autoformatting tool:
  https://black.readthedocs.io/en/stable/index.html (:merge:`1028`, :merge:`1030`). By `Kyle Brindley`_.
- Simplify the pytest commands by always running the XML/HTML coverage (:merge:`1034`). By `Kyle Brindley`_.

Enhancements
============
- Verify parameter set hash coordinates when reading user supplied previous parameter study files (:issue:`825`,
  :merge:`1032`, :merge:`1035`). By `Kyle Brindley`_.

*******************
0.12.2 (2024-11-14)
*******************

New Features
============
- Add Abaqus pseudo-builder (:issue:`659`, :merge:`825`). By `Matthew Fister`_.
- Add a simple command line utility to print project managed parameter study files (:merge:`1021`). By `Kyle Brindley`_.

Bug fixes
=========
- Do not modify suffixes list in the Abaqus solver emitter (:merge:`1012`). By `Kyle Brindley`_.

Documentation
=============
- Update tutorial output file expectations to match the switch from the Abaqus journal builder to the Abaqus journal
  builder factory (:issue:`817`, :merge:`1011`). By `Kyle Brindley`_.
- HTML and PDF documentation formatting (:merge:`1012`). By `Kyle Brindley`_.
- Add missing pytest package to tutorial environment instructions for unit testing tutorial (:merge:`1012`). By `Kyle
  Brindley`_.
- Make the tutorial visualization images click-to-expand (:merge:`1016`). By `Kyle Brindley`_.
- Add a mesh convergence parameter study to the WAVES quickstart and discuss the benefits of using a build system and
  WAVES for computational science and engineering workflows (:merge:`1019`, :merge:`1022`). By `Kyle Brindley`_.
- Add a quick print utility to the WAVES quickstart tutorial to help show set numbering behaviors (:merge:`1021`,
  :merge:`1023`, :merge:`1024`). By `Kyle Brindley`_.
- Add HTML coverage report to internally hosted Gitlab-Pages documentation (:merge:`1024`). By `Kyle Brindley`_.

Internal Changes
================
- Add Python 3.13 and SCons 4.8 to the Conda build test matrix in the scheduled CI jobs (:issue:`820`, :merge:`1015`).
  By `Kyle Brindley`_.
- Simplify pytest coverage report command construction (:merge:`1024`). By `Kyle Brindley`_.

Enhancements
============
- Always perform individual simulation post-processing in modsim templates. Matches modsim template 1 simulation
  post-processing behavior to modsim template 2 (:merge:`1016`). By `Kyle Brindley`_.

*******************
0.12.1 (2024-11-06)
*******************

New Features
============
- Add function for printing the action signature string for targets (:issue:`810`, :merge:`999`). By `Kyle Brindley`_.

Documentation
=============
- Hyperlink specific portions of the SCons man page instead of quoting (:merge:`998`). By `Kyle Brindley`_.
- Fix version number display when building with ``sphinx_rtd_theme`` version 3 (:issue:`808`, :merge:`1004`). By `Kyle
  Brindley`_.
- Add more acronyms to glossary and add copyright years as a range (:merge:`1005`). By `Kyle Brindley`_.
- Build and host the modsim-template documentation on GitHub-Pages (:issue:`813`, :merge:`1006`). By `Kyle Brindley`_.
- Update Sphinx HTML theme, landing page contents, and build the modsim-template documentation for GitHub-Pages
  (:merge:`1007`). By `Kyle Brindley`_.

Internal Changes
================
- Refactor the parameter study write functions for greater consistency with the parameter study to dictionary function
  and greater consistency between write method output file name lists (:issue:`811`, :merge:`1000`). By `Kyle
  Brindley`_.
- Unify the parameter study write-to-file logic in a single function (:merge:`1002`). By `Kyle Brindley`_.
- Add new Sphinx theme packages to CI environment (:issue:`815`, :merge:`1009`). By `Kyle Brindley`_.

Enhancements
============
- Allow parameter generator ``write`` method API override for output file type (:merge:`1001`). By `Kyle Brindley`_.

*******************
0.12.0 (2024-10-17)
*******************

.. warning::

   The ``quantiles`` removal from parameter generator objects will cause parameter set index changes for stochastically
   sampled parameter generators, e.g. ``SALib`` and ``SciPy`` based generators. Parameter studies generated with this
   version may not merge correctly with parameter studies from older versions of WAVES even if the parameter sets have
   not changed. It is strongly recommended that users re-generate their parameter study files.

Breaking changes
================
- Remove the ``quantiles`` data from parameter generators and parameter study objects. Required to allow typed parameter
  data arrays and greater type flexibility when writing parameter studies to H5 files (:issue:`794`, :merge:`975`). By
  `Kyle Brindley`_.
- Remove the ``data_type`` coordinate from parameter generators and parameter study objects. Required to allow typed
  parameter data arrays and greater type flexibility when writing parameter studies to H5 files (:issue:`765`,
  :merge:`986`). By `Kyle Brindley`_.
- Remove semi-private ``_ParameterGenerator`` class. ``ParameterGenerator`` class is now part of the public API
  (:issue:`791`, :merge:`988`). By `Kyle Brindley`_.
- Deprecate the ``postfix`` key word argument across all functions (:issue:`724`, :merge:`989`). By `Kyle Brindley`_.
- Deprecate the substitution dictionary first positional argument interface for ``substitution_syntax`` function. New
  argument order is ``(env, substitution_dictionary, **kwargs)``. The ``env`` positional argument may be omitted when
  using the function as an SCons method. See the API and examples (:issue:`764`, :merge:`992`). By `Kyle Brindley`_.
- Deprecate the ``copy_substitute`` function in favor or ``copy_substfile`` (:issue:`665`, :merge:`990`). `Kyle
  Brindley`_.
- Deprecate the ``python_script`` builder in favor of ``python_builder_factory`` (:issue:`747`, :merge:`993`). By `Kyle
  Brindley`_.
- Deprecate the ``quinoa_solver`` builders in favor of the ``quinoa_solver_builder_factory`` (:issue:`745`,
  :merge:`991`). By `Kyle Brindley`_.
- Deprecate the ``quinoa_solver`` builders in favor of the ``quinoa_builder_factory`` (:issue:`745`, :merge:`991`). By
  `Kyle Brindley`_.
- Deprecate the ``(names, env)`` argument order in program finding functions. New argument order is ``(env, names)`` for
  SCons ``AddMethod`` compatibility (:issue:`755`, :merge:`994`). By `Kyle Brindley`_.
- Deprecate the ``(print_stdout)`` interface of ``print_build_failures`` in favor of the SCons ``AddMethod`` compatible
  ``(env, print_stdout)`` interface (:issue:`758`, :merge:`995`). By `Kyle Brindley`_.

Enhancements
============
- Preserve parameter types and handle booleans when writing parameter study objects to disk (:issue:`765`,
  :merge:`986`). By `Kyle Brindley`_.

Internal Changes
================
- Drop Python 3.8 support and testing for end-of-life support. New minimum supported version of Python is 3.9
  (:issue:`770`, :merge:`987`). By `Kyle Brindley`_.
- Temporary CI environments for MacOS CI pipelines to avoid simultaneous pipelines clobbering a common environment
  (:issue:`809`, :merge:`996`). By `Kyle Brindley`_.

*******************
0.11.6 (2024-10-15)
*******************

New Features
============
- Add a CalculiX builder factory (:merge:`984`). By `Kyle Brindley`_.

Documentation
=============
- Add a WIP Gmsh+CalculiX tutorial outline (:issue:`807`, :merge:`985`). By `Kyle Brindley`_.

Internal Changes
================
- Run the pytest alias during Windows CI ``pwsh`` job (:issue:`799`, :merge:`971`). By `Kyle Brindley`_.
- Run an experimental MacOS CI pipeline (:issue:`800`, :merge:`972`). By `Kyle Brindley`_.
- Make the system tests more graceful when testing on systems without necessary third-party software, while still
  allowing unconditional forced builds for internal Linux CI servers (:issue:`737`, :merge:`973`). By `Kyle Brindley`
- Skip documentation PDF build when ``latexmk`` is not found. Allow override to force build on appropriate CI servers
  (:issue:`795`, :merge:`974`). By `Kyle Brindley`_.
- Remove deprecated ``elasticity3D.xml`` file from Fierro tutorials (:issue:`804`, :merge:`976`). By `Kyle Brindley`_.
- Add CalculiX, ccx2paraview, and ParaView conda-forge packages to CI environment (:issue:`806`, :merge:`977`). By `Kyle
  Brindley`_.
- Convert Gmsh tutorial to a Gmsh+CalculiX tutorial in pursuit of a fully open-source, conda-forge workflow
  (:issue:`805`, :merge:`979`). By `Kyle Brindley`_.
- Create unique, temporary Windows CI environments for clean environments in every pipeline (:merge:`982`). By `Kyle
  Brindley`_.
- Add simple post-processing to Gmsh+CalculiX tutorial. Now using ccx2paraview and meshio packages to convert to xarray
  (:merge:`983`). By `Kyle Brindley`_.

*******************
0.11.5 (2024-10-08)
*******************

Bug fixes
=========
- Handle carriage returns in visualize line split. Fixes visualize graph node names on Windows (:issue:`788`,
  :merge:`962`). By `Kyle Brindley`_.
- Handle Windows caveats to opening temporary files. Fixes the Abaqus CAE and modsim template Abaqus Python scripts that
  use ``tempfile`` and ``shutil.copy`` together (:issue:`798`, :merge:`969`). By `Kyle Brindley`_.

Internal Changes
================
- Set build environment variable ``PYTHONDONTWRITEBYTECODE`` in construction environment instead of pytest task
  commands. Fixes pytest task for Windows development and execution (:issue:`788`, :merge:`962`). By `Kyle Brindley`_.
- Add Windows CI environment file, removing non-Windows compatible packages. Add Windows CI pipeline (:issue:`788`,
  :merge:`962`). By `Kyle Brindley`_.
- Limit flake8 parallelism to avoid multiprocessing bug on Windows (:issue:`788`, :merge:`962`). By `Kyle Brindley`_.

*******************
0.11.4 (2024-10-07)
*******************

Bug fixes
=========
- Remove duplicate parameter value definitions in tutorials nominal parameter set definition (:issue:`785`,
  :merge:`958`). By `Kyle Brindley`_.

Documentation
=============
- Add the writing builders solver script API/CLI to the tutorial API/CLI HTML documentation (:merge:`953`). By `Kyle
  Brindley`_.

Internal Changes
================
- Recipe maintenance to address feedback from conda-forge reviewers (:issue:`779`, :merge:`949`). By `Kyle Brindley`_.
- Clean up PIP and Conda package builds to exclude project build files for all package builds and system test artifacts
  for working repository package builds (:merge:`950`). By `Kyle Brindley`_.
- Reduce usage of ``/tmp`` and ``$TMPDIR`` for system testing because some tests require executable permissions in the
  test working directory (:merge:`953`). By `Kyle Brindley`_.
- Set package runtime minimum version of SCons to match major version ``>=4`` (:merge:`953`). By `Kyle Brindley`_.
- Use pathlib objects in project build scripts. Update minimum build requirement for SCons to match ``>=4.6``
  (:merge:`953`). By `Kyle Brindley`_.
- Add gmsh to CI environment (:issue:`783`, :merge:`955`). By `Kyle Brindley`_.
- Add the source files for a WIP Gmsh tutorial matching the WAVES quickstart (:issue:`782`, :merge:`954`). By `Kyle
  Brindley`_.
- Update to the newest AEA shared compute environment naming convention. Remove outdated environment discussion
  (:issue:`778`, :merge:`956`). By `Kyle Brindley`_.
- Allow Abaqus CAE tutorial workflow to ignore all Abaqus tasks when Abaqus is missing (:issue:`781`, :merge:`957`). By
  `Kyle Brindley`_.

Enhancements
============
- Bundle built HTML and man page documentation with Gitlab PyPI registry package (:issue:`780`, :merge:`951`,
  :merge:`952`). By `Kyle Brindley`_.
- Add unit tests for the modsim template's parameter sets module (:issue:`785`, :merge:`958`). By `Kyle Brindley`_.
- Add type hints, re-usable entity recovery by coordinates function, and global seed API/CLI to Gmsh tutorial files
  (:merge:`959`, :merge:`960`). By `Kyle Brindley`_.
- Expose the WAVES ParameterGenerator abstract base class (ABC) to the public API for officially supported type checking
  (:issue:`789`, :merge:`961`). By `Kyle Brindley`_.
- Dedicated regression test script in tutorials and modsim templates (:issue:`790`, :merge:`963`). By `Kyle Brindley`_.
- Use the ``ParameterStudySConscript`` feature in modsim template 2 for reduced task duplication (:issue:`787`,
  :merge:`964`). By `Kyle Brindley`_.
- Handle missing previous parameter study files gracefully with a warning. Users relying on the ``RuntimeError``
  behavior may re-enable this behavior with the ``require_previous_parameter_study=True`` API or
  ``--require-previous-parameter-study`` CLI options.

*******************
0.11.3 (2024-09-24)
*******************

Documentation
=============
- Replace ``touch`` commands with ``waves fetch`` commands in tutorials for better Windows Powershell compatibility
  (:issue:`772`, :merge:`942`). By `Kyle Brindley`_.
- Add LANL HPC path options to tutorial third-party software installation paths (:issue:`596`, :merge:`943`). By `Kyle
  Brindley`_.
- Move the ``modsim_template_2`` the parameter study configuration artifacts from the source tree to the build tree
  (:merge:`947`). By `Kyle Brindley`_.

Internal Changes
================
- Use a single type of string substitution in system test command construction (:issue:`768`, :merge:`935`). By `Kyle
  Brindley`_.
- Update the Fierro FE solver Conda package name (:issue:`766`, :merge:`936`). By `Kyle Brindley`_.
- Update LANL HPC server references (:issue:`767`, :merge:`934`). By `Kyle Brindley`_.
- Provide finer grained system test controls to allow running WAVES-only system tests, e.g. WAVES CLI tests, in external
  recipe builds (:issue:`769`, :merge:`937`, :merge:`938`). By `Kyle Brindley`_.
- Remove conda-verify from GitHub workflows because it appears to cause CI environment errors (:merge:`940`). By `Kyle
  Brindley`_.
- Run a full matrix of Python and SCons version tests during scheduled CI testing, patch unit test construction for
  Python <=3.10, fix Python 3.8 type hint compatibility (:issue:`771`, :merge:`939`). By `Kyle Brindley`_.
- Add HPC system tests, but do not depend on them for passing merge-requests (:issue:`596`, :merge:`943`). By `Kyle
  Brindley`_.
- Remove unconditional build from Cubit+Sierra tutorial system tests because they can not pass on HPC CI pipelines.
  Partial system test on HPC is more valuable than strictly enforced test of fragile third-party installation
  (:issue:`773`, :merge:`944`). By `Kyle Brindley`_.
- Update setuptools version specs to match current setuptools_scm documentation (:issue:`777`, :merge:`946`). By `Kyle
  Brindley`_.

*******************
0.11.2 (2024-08-29)
*******************

New Features
============
- Add first target builder factory style builders to the WAVES SCons environment class (:issue:`762`, :merge:`933`). By
  `Kyle Brindley`_.

Bug fixes
=========
- Fix the Abaqus journal builder factory CAE options syntax (:issue:`762`, :merge:`933`). By `Kyle Brindley`_.

Documentation
=============
- Use the WAVES SCons environment in the tutorials and modsim template (:issue:`762`, :merge:`933`). By `Kyle
  Brindley`_.

*******************
0.11.1 (2024-08-28)
*******************

Breaking changes
================
- Add a construction environment argument to the ``substitution_syntax`` method for compatibility with SCons
  ``AddMethod``. Backward compatibility is maintained with a syntax warning and instructions for what to change for v1
  (:issue:`759`, :merge:`932`). By `Kyle Brindley`_.

New Features
============
- Add a check program function similar to SCons CheckProg, but without the SCons Configure object (:merge:`929`). By
  `Kyle Brindley`_.
- Add a WAVES SCons environment class to provide common methods and reduce configuration boilerplate (:issue:`756`,
  :merge:`929`). By `Kyle Brindley`_.
- Add a ParameterStudySConscript wrapper to unpack parameter generators into SConscript calls (:issue:`761`,
  :merge:`930`). By `Kyle Brindley`_.
- Add ``SubstitutionSyntax`` method to WAVES SCons environment class (:issue:`759`, :merge:`932`). By `Kyle Brindley`_.

Documentation
=============
- Convert all SConscript ``exports=`` arguments to dictionary style for more explicit control over exports
  and greater consistency with ParameterStudySConscript interface requirements (:issue:`763`, :merge:`931`). By `Kyle
  Brindley`_.

Internal Changes
================
- Avoid SCons Configure() method when searching for programs in construction environments. Fixes the program operations
  unit test interference with builder unit tests (:merge:`929`). By `Kyle Brindley`_.

*******************
0.11.0 (2024-08-26)
*******************

Breaking changes
================
- Re-write the Fierro builders to use the template first target builder factory. Builders are still considered
  experimental as the Fierro CLI stabilizes, so no minor version bump for the builder name and API change (:issue:`743`,
  :merge:`913`). By `Kyle Brindley`_.
- Re-write the Ansys APDL builder to use the template first target builder factory. Builder is still considered
  experimental pending a system test and user feedback, so no minor version bump for the builder name and API change
  (:issue:`742`, :merge:`914`). By `Kyle Brindley`_.
- Re-write the Sierra builder to use the template first target builder factory. Builder is still considered experimental
  pending user feedback, so no minor version bump for the builder name and API change (:issue:`744`, :merge:`916`). By
  `Kyle Brindley`_.
- Re-order the program operation function arguments for compatibility with SCons ``AddMethod``. Backward compatibility
  is maintained with a syntax warning and instructions for what to change for v1 (:issue:`754`, :merge:`925`). By `Kyle
  Brindley`_.
- Add a construction environment argument to the ``print_build_failures`` method for compatibility with SCons
  ``AddMethod``. Backward compatibility is maintained with a syntax warning and instructions for what to change for v1
  (:issue:`757`, :merge:`927`). By `Kyle Brindley`_.

New Features
============
- Expose the most common "first target emitter" to the public API (:issue:`718`, :merge:`906`). By `Kyle Brindley`_.
- Add template builder factories with |PROJECT| style action string construction and common emitter behavior
  (:issue:`718`, :merge:`906`). By `Kyle Brindley`_.
- Rename the first target builder (factory) to clarify that this function returns a builder. Clarify that the first
  target emitter is not a factory and that the keyword arguments can not be used directly in a builder definition
  (:issue:`738`, :merge:`910`). By `Kyle Brindley`_.
- Add a Quinoa builder factory based on the first target builder factory template (:issue:`739`, :merge:`911`). By `Kyle
  Brindley`_.
- Add a Python builder factory based on the first target builder factory template (:issue:`741`, :merge:`915`). By `Kyle
  Brindley`_.
- Add an SBatch Quinoa builder factory (:issue:`740`, :merge:`917`). By `Kyle Brindley`_.
- Add an SBatch Python builder factory (:issue:`746`, :merge:`918`). By `Kyle Brindley`_.
- Add an Abaqus journal builder factory based on the first target builder factory template (:issue:`748`, :merge:`921`).
  By `Kyle Brindley`_.
- Add an Abaqus solver builder factory based on the first target builder factory template (:issue:`749`, :merge:`922`).
  By `Kyle Brindley`_.

Documentation
=============
- In the mesh convergence tutorial and modsim templates, SCons joins list variables as space separated strings. No need
  to join lists of strings separately from task definition (:issue:`734`, :merge:`907`). By `Kyle Brindley`_.
- Update the tutorials to use the Python builder factory (:issue:`741`, :merge:`915`). By `Kyle Brindley`_.
- Update the tutorials to use the Sierra builder factory (:issue:`744`, :merge:`916`). By `Kyle Brindley`_.
- Add deprecation warnings to the older pattern Quinoa builders (:issue:`740`, :merge:`917`). By `Kyle Brindley`_.
- Add deprecation warnings to the older pattern Python builders (:issue:`746`, :merge:`918`). By `Kyle Brindley`_.
- Update the tutorials and modsim templates to use the SCons ``AddMethod`` style access for project help messages
  (:issue:`753`, :merge:`924`). By `Kyle Brindley`_.
- Add a work-in-progress tutorial for writing builders (:issue:`727`, :merge:`926`). By `Kyle Brindley`_.

Internal Changes
================
- Re-enable the Quinoa CI system tests (:issue:`657`, :merge:`919`). By `Kyle Brindley`_.
- Consolidate builder factory tests under a single test function (:issue:`750`, :merge:`923`). By `Kyle Brindley`_.

Enhancements
============
- Support SCons construction environment recovery for more than just bash. Explicit support for: sh, bash, zsh, csh,
  tcsh (:issue:`735`, :merge:`908`, :issue:`736`, :merge:`909`). By `Kyle Brindley`_.
- Improve the help message functions environment handling for use with SCons ``AddMethod`` (:issue:`753`, :merge:`924`).
  By `Kyle Brindley`_.

*******************
0.10.0 (2024-08-15)
*******************

Breaking changes
================
- Change the Conda environment action options from ``conda_env_export_options`` to ``options`` for improved builder
  action string keyword argument consistency (:issue:`719`, :merge:`889`). By `Kyle Brindley`_.
- Change the Fierro and Ansys APDL action prefix and suffix options for improved builder action string keyword argument
  consistency (:issue:`709`, :merge:`890`). By `Kyle Brindley`_.
- Update the default ``construct_action_list`` prefix string to match builder factories' action string updates
  (:issue:`716`, :merge:`895`). By `Kyle Brindley`_.
- Re-arrange the Abaqus solver's required options in the action string to move closer to a standardized action string
  template across all builders. Will cause Abaqus solver tasks to re-build for the new action signature. Does *not*
  change the default Abaqus options (:issue:`723`, :merge:`896`). By `Kyle Brindley`_.
- Replace 'postfix' name with 'suffix' in function keyword argument APIs for better consistency with builder action
  construction naming conventions. Maintains 'postfix' keyword arguments with a v1 deprecation warning in this version
  (:issue:`722`, :merge:`897`). By `Kyle Brindley`_.
- Remove the largely unused ``post_action`` builder behavior in favor of more modifiable builders and action modifier
  functions. Similar behavior can be provided on a per-target basis with the `SCons AddPostAction`_ feature
  (:issue:`725`, :merge:`898`). By `Kyle Brindley`_.
- Replace the rsync options with a keyword argument in the  SSH builder actions (:issue:`728`, :merge:`899`). By `Kyle
  Brindley`_.

New Features
============
- Add a function to convert a builder's action list to a list of strings (:issue:`721`, :merge:`892`). By `Kyle
  Brindley`_.
- Add a function to convert a list of action strings to an SCons ListAction object (:issue:`721`, :merge:`892`). By
  `Kyle Brindley`_.

Bug fixes
=========
- Remove unnecessary single quotes in task definition shell commands. Fixes errors in Windows Powershell tutorial
  execution (:issue:`717`, :merge:`882`). By `Kyle Brindley`_.
- Fix recursive search for Cubit bin directory (:merge:`894`). By `Kyle Brindley`_.
- Allow Cubit+ tutorials to run when Sierra is not installed (:merge:`894`). By `Kyle Brindley`_.

Documentation
=============
- Improved inclusion of inherited, public methods in the external API (:issue:`706`, :merge:`880`). By `Kyle Brindley`_.
- Add LANL specific installation instruction to internal HTML documentation build. By `Kyle Brindley`_.

Internal Changes
================
- Test per-task action string keyword argument overrides (:issue:`720`, :merge:`891`). By `Kyle Brindley`_.
- Inline the action prefix for builder factory actions for more obvious unit test expectations (:issue:`721`,
  :merge:`892`). By `Kyle Brindley`_.
- Add the documentation index file path to the docs subcommand internal API (:issue:`730`, :merge:`901`). By `Kyle
  Brindley`_.
- Use a common downstream pipeline to deploy to the internal conda channel (:issue:`733`, :merge:`904`). By `Kyle
  Brindley`_.

Enhancements
============
- Expose the Abaqus journal action keyword arguments to the constructor API and task definition for greater flexibility
  in constructed builder behavior (:issue:`708`, :merge:`881`). By `Kyle Brindley`_.
- Expose the Abaqus solver action keyword arguments to the constructor API and task definitions for greater flexibility
  in constructed builder behavior (:issue:`710`, :merge:`883`). By `Kyle Brindley`_.
- Expose the Sierra action keyword arguments to the constructor API and task definitions for greater flexibility in
  constructed builder behavior (:issue:`711`, :merge:`885`). By `Kyle Brindley`_.
- Expose the Python script action keyword arguments to the constructor API and task definitions for greater flexibility
  in constructed builder behavior (:issue:`712`, :merge:`886`). By `Kyle Brindley`_.
- Expose the Matlab script action keyword arguments to the constructor API and task definitions for greater flexibility
  in constructed builder behavior (:issue:`713`, :merge:`887`). By `Kyle Brindley`_.
- Expose the SLURM sbatch action keyword arguments to the constructor API and task definitions for greater flexibility
  in constructed builder behavior (:issue:`715`, :merge:`888`). By `Kyle Brindley`_.
- Expose the Conda environment export action keyword arguments to the constructor API and task definitions for greater
  flexibility in constructed builder behavior (:issue:`719`, :merge:`889`). By `Kyle Brindley`_.
- Expose the Fierro and Ansys APDL action keyword arguments to the constructor API and task definitions for greater
  flexibility in constructed builder behavior (:issue:`709`, :merge:`890`). By `Kyle Brindley`_.
- Expose the Quinoa action keyword arguments to the constructor API and task definitions for greater flexibility in
  constructed builder behavior (:issue:`714`, :merge:`893`). By `Kyle Brindley`_.
- Expose the SSH builder actions keyword arguments to the constructor API and task definitions for greater flexibility
  in constructed builder behavior (:issue:`728`, :merge:`899`). By `Kyle Brindley`_.

******************
0.9.5 (2024-07-25)
******************

Bug fixes
=========
- Fix the Windows installation CLI entry points and add the conda-build preferred entry points recipe entry
  (:issue:`703`, :merge:`877`). By `Kyle Brindley`_.

Documentation
=============
- Return the Python method section headers to the HTML sidebar while preserving a cleaner PDF index without the Python
  methods (:issue:`702`, :merge:`875`). By `Kyle Brindley`_.

Internal Changes
================
- Update unit tests for inconsistent pathlib path seps in Windows Powershell execution. Larger refactor required for
  improved robustness in building expected results or converting all paths to UNIX style path seps (:merge:`876`). By
  `Kyle Brindley`_.
- Add CI test for the external conda-build recipe (:issue:`703`, :merge:`877`). By `Kyle Brindley`_.
- Add Windows CI build/test for new tags in GitHub Actions. Update all GitHub Actions to use miniforge for reduced
  environment changes after configuration (:issue:`704`, :merge:`878`). By `Kyle Brindley`_.
- Update remaining unit test Windows path expectations for Windows absolute paths (:issue:`705`, :merge:`879`). By `Kyle
  Brindley`_.

******************
0.9.4 (2024-07-18)
******************

Documentation
=============
- Clean up the index by removing the Python method entries (:issue:`699`, :merge:`873`). By `Kyle Brindley`_.
- Update the GitHub URLs for the migration to https://github.com/lanl-aea (:issue:`700`, :merge:`874`).  By `Kyle
  Brindley`_.

******************
0.9.3 (2024-07-11)
******************

Internal Changes
================
- Build the pip package with ``matplotlib`` as a dependency because PyPI doesn't have a ``matplotlib-base`` package
  (:issue:`698`, :merge:`872`). By `Kyle Brindley`_

******************
0.9.2 (2024-07-10)
******************

Internal Changes
================
- Remove conda channel index from CI deployment job. Can't separate the CI environment and continue to index the shared
  conda channel (:issue:`695`, :merge:`868`). By `Kyle Brindley`_.
- Use both AEA Gitlab-Runner servers in CI jobs (:issue:`696`, :merge:`869`). By `Kyle Brindley`_.
- Experimental Gitlab PyPI registry deployment (:merge:`870`). By `Kyle Brindley`_.

******************
0.9.1 (2024-07-01)
******************

Bug fixes
=========
- Fix the namespace of the example argparse types script in the tutorial and modsim template (:issue:`683`,
  :merge:`861`). By `Kyle Brindley`_.

Documentation
=============
- Add discussion about modsim template trade-offs and features (:issue:`687`, :merge:`865`). By `Kyle Brindley`_.
- Re-write the Fierro tutorial as a Cubit+Fierro tutorial. Made possible with a mesh conversion script
  originally authored by Evan Lieberman and modified to add WAVES style CLI (:issue:`681`, :merge:`859`). By `Kyle
  Brindley`_.

New Features
============
- Draft experimental parameter study pseudo-builder as one option for task re-use without task duplication. Intended to
  reduce the nominal/mesh convergence examples to a single workflow file (:issue:`680`, :merge:`858`). By `Kyle
  Brindley`_.
- Add argparse type checker unit test example to the modsim template (:issue:`683`, :merge:`861`). By `Kyle Brindley`_.
- Re-use the part and simulation task definitions in the modsim template workflows (:issue:`684`, :merge:`862`). By
  `Kyle Brindley`_.
- Add modsim template with advanced features to reduce configuration verbosity (:issue:`687`, :merge:`865`). By `Kyle
  Brindley`_.

Internal Changes
================
- Add meshio to CI environment for mesh conversion workflows, e.g. a future Cubit+Fierro tutorial (:issue:`681`,
  :merge:`859`). By `Kyle Brindley`_.
- Restrict CI and tutorial environments to numpy <2 until SALib is compatible or packaged with an upper-bound
  (:issue:`685`, :merge:`863`). By `Kyle Brindley`_.
- Improve robustness against changing parameter study set order in unit tests (:issue:`683`, :merge:`861`). By `Kyle
  Brindley`_.

******************
0.9.0 (2024-05-29)
******************

Breaking changes
================
- Remove click event matplotlib behavior broken since :ref:`0.8.6`. Allows reduced plot annotations for smaller image
  sizes (:merge:`845`). By `Kyle Brindley`_.
- Change API/CLI options from ``dryrun`` to ``dry_run`` and ``--dry-run``, respectively, for greater PEP-8 and SCons
  consistency (:issue:`671`, :merge:`846`). By `Kyle Brindley`_.

Bug fixes
=========
- Visualize subgraph by targets when provided an SCons tree file (:issue:`676`, :merge:`854`). By `Kyle Brindley`_.

Internal Changes
================
- Move remaining module constants into package settings (:issue:`673`, :merge:`848`). By `Kyle Brindley`_.
- Use full namespace in submit CAE tutorial journal file. Add a feature to write an input file and exit instead of
  submitting the job (:merge:`852`). By `Kyle Brindley`_.
- Re-enable the Fierro tutorial system tests (:issue:`638`, :merge:`856`). By `Kyle Brindley`_.

Enhancements
============
- Improve consistency between plot and graphml output for the visualize subcommand (:merge:`845`). By `Kyle Brindley`_.
- Add options to change plot colors in visualize plot output (:issue:`667`, :merge:`847`). By `Kyle Brindley`_.
- Try to catch CLI typos in the tutorial and modsim template Abaqus journal files (:issue:`675`, :merge:`853`). By
  `Kyle Brindley`_.
- Accept multiple targets in visualize subcommand. More closely match visualize/build CLI pass through behavior
  (:issue:`676`, :merge:`854`). By `Kyle Brindley`_.
- Add MPI run executable and options to the Fierro builder (:issue:`638`, :merge:`856`). By `Kyle Brindley`_.

.. _0.8.6:

******************
0.8.6 (2024-05-16)
******************

Documentation
=============
- Add example usage for print build failures function (:issue:`670`, :merge:`833`). By `Kyle Brindley`_.
- Break long API function signatures into multiple lines for better readability (:merge:`835`) By `Kyle Brindley`_.
- Add a tutorial for integrating interactively edited CAE files with a build system (:issue:`497`, :merge:`839`,
  :merge:`840`). By `Kyle Brindley`_.

Internal Changes
================
- Use networkx built-in graphml writer (:issue:`672`, :merge:`838`). By `Kyle Brindley`_.
- Remove unused and redundant pytest markers (:issue:`672`, :merge:`838`). By `Kyle Brindley`_.
- Add minimal and sign-of-life unit tests for more of the visualize subcommand implementation (:issue:`672`,
  :merge:`838`). By `Kyle Brindley`_.

Enhancements
============
- Change the parameter generator API deafult output file type H5 files. Matches tutorial behavior to default behavior
  for reduced configuration during preferred usage (:merge:`834`). By `Kyle Brindley`_.
- Better consistency in ``--dry-run`` option string, as opposed to ``--dryrun`` (:merge:`836`). By `Kyle Brindley`_.
- Add an option for transparent backgrounds in the visualize images (:issue:`669`, :merge:`837`). By `Kyle Brindley`_.

******************
0.8.5 (2024-05-09)
******************

New Features
============
- Add a copy substfile pseudo-builder as a replacement for the ``copy_substitute`` method. Pseudo-builders use the same
  access syntax as SCons builders and are the recommended solution for wrapping builders with advanced behaviors
  (:issue:`662`, :merge:`829`). By `Kyle Brindley`_.

Bug fixes
=========
- Always write both ``odb_extract`` output files: ``output_file.h5`` and ``output_file_datasets.h5`` for more
  predictable behavior in programmatic workflows, e.g. the abaqus extract builder (:issue:`478`, :merge:`830`). By `Kyle
  Brindley`_.

Documentation
=============
- Release the sensitivity study as a supplemental lesson (:issue:`643`, :merge:`820`). By `Kyle Brindley`_.
- Add a warning about whitespace in SCons command line options in the first tutorial (:merge:`821`). By `Kyle
  Brindley`_.
- Update all tutorials and the modsim template to use a copy substitute pseudo-builder instead of the
  ``copy_substitute`` function. Pseudo-builders use the same access syntax as SCons builders and are the recommended
  solution for wrapping builders with advanced behaviors (:issue:`662`, :merge:`829`). By `Kyle Brindley`_.
- Improve the formatting of the odb extract help message (:issue:`478`, :merge:`830`). By `Kyle Brindley`_.

Internal Changes
================
- Activate project CI environment directly. Fixes errors related to conda-build/boa/mambabuild during packaging
  (:merge:`823`). By `Kyle Brindley`_.
- Skip Matlab system test because there are too few licenses for reliable execution (:merge:`824`). By `Kyle Brindley`_.
- Update the tutorial journal files for better compliance with PEP-8. Use Abaqus Python API for rectangle sketch
  generation (:issue:`661`, :merge:`826`). By `Kyle Brindley`_.
- Add lazy loader package to CI environment for testing (:issue:`664`, :merge:`827`). By `Kyle Brindley`_.
- Handle file extensions in the tutorial and modsim template Abaqus and Cubit journal files (:issue:`663`,
  :merge:`828`). By `Kyle Brindley`_.

Enhancements
============
- Add an option to annotate the visualize output with the number of nodes (:issue:`654`, :merge:`822`). By `Kyle
  Brindley`_.
- More robust regression testing function in tutorials and modsim template (:issue:`666`, :merge:`831`). By `Kyle
  Brindley`_.

******************
0.8.4 (2024-05-01)
******************

Bug fixes
=========
- Fix Python 3.8 and 3.9 incompatibility introduced in :ref:`0.7.10` (:merge:`749`) with Python 3.8 compatible type
  annotations (:issue:`650`, :merge:`809`). By `Kyle Brindley`_.
- Search for the default target naming convention when printing failed node STDOUT files (:issue:`648`, :merge:`814`).
  By `Kyle Brindley`_.

Documentation
=============
- Fix broken abaqus links (:issue:`642`, :merge:`805`). By `Sergio Cordova`_.
- Add part image supplemental lesson (:issue:`570`, :merge:`797`). By `Sergio Cordova`_.

Internal Changes
================
- Switch to flake8 for style checking and address line length and whitespace errors (:issue:`649`, :merge:`806`). By
  `Kyle Brindley`_.
- Use an SCons task to drive flake8 more consistently with other project tasks (:merge:`807`). By `Kyle Brindley`_.
- Separate modsim template workflow results from intermediate build artifacts to clean up workflow visualization
  (:issue:`651`, :merge:`808`). By `Kyle Brindley`_.
- Resolved all static type checks in the ``_fetch`` and ``_visualize`` internal modules (:merge:`811`). By `Kyle
  Brindley`_.
- Update Fierro builder to account for change in executable name(s)/CLI (:issue:`647`, :merge:`812`). By `Kyle
  Brindley`_.
- Add mypy static type checking configuration file for better consistency between CI and developer execution
  (:issue:`653`, :merge:`813`). By `Kyle Brindley`_.
- Add Quinoa Solver builder unit tests (:issue:`561`, :merge:`815`). By `Kyle Brindley`_.
- Match GitHub (external) recipe test commands to internal recipe test commands (:merge:`817`). By `Kyle Brindley`_.
- Report YAML loading syntax errors with a message and non-zero exit code instead of a stack trace (:issue:`658`,
  :merge:`819`). By `Kyle Brindley`_.

******************
0.8.3 (2024-04-10)
******************

Bug fixes
=========
- Remove unused kwargs arguments to improve API error reporting in builders. Argument no longer used after :issue:`508`
  and :merge:`779` as part of the keyword argument standardization (:issue:`646`, :merge:`803`). By `Kyle Brindley`_.

******************
0.8.2 (2024-04-10)
******************

.. warning::

   Due to a bugfix in parameter set indexing, parameter studies generated with this version may index as new parameter
   sets on merge with parameter studies from older versions of WAVES even if the parameter sets have not changed. It is
   strongly recommended that users re-generate their parameter study files.

New Features
============
- Draft experimental Fierro builders and add associated draft tutorial (:issue:`637`, :merge:`796`). By `Kyle
  Brindley`_.
- Draft experimental Ansys APDL builder (:issue:`800`). By `Kyle Brindley`_.

Bug fixes
=========
- Sort parameter set definitions by parameter name for hash index creation. Fixes an edge case where the parameters are
  re-arranged causing the set to appear new even if the set definition is otherwise identical. Parameter study indices may
  be inconsistent with prior versions of WAVES (:issue:`645`, :merge:`802`). By `Kyle Brindley`_.

Internal Changes
================
- Remove the upper bound version of setuptools_scm and use the latest version in the CI environment (:issue:`635`,
  :merge:`794`). By `Kyle Brindley`_.
- Add ``FierroMechanics`` channel and ``fierro-cpu`` to CI compute environment in preparation for draft Fierro builder
  support (:issue:`636`, :merge:`795`). By `Kyle Brindley`_.
- Separate subcommand implementations into supporting modules for reduced clutter in main CLI implementation
  (:issue:`641`, :merge:`798`). By `Kyle Brindley`_.

******************
0.8.1 (2024-04-01)
******************

.. warning::

   Due to a bugfix in parameter set indexing, parameter studies generated with this version will index as new parameter
   sets on merge with parameter studies from older versions of WAVES even if the parameter sets have not changed. It is
   strongly recommended that users re-generate their parameter study files.

Bug fixes
=========
- Handle STDIN YAML formatted string, file paths, and missing input cases for parameter study CLI (:issue:`632`,
  :merge:`792`). By `Kyle Brindley`_.
- Add parameter names and quantiles to the parameter set hash to guarantee unique parameter set index on changes. Fixes
  an edge case where a parameter name changes, but the set content may appear identical. Parameter study indices will be
  inconsistent with prior versions of WAVES (:issue:`633`, :merge:`793`). By `Kyle Brindley`_.

Enhancements
============
- Raise a more useful exception/error message when a previous parameter study file does not exists (:issue:`631`,
  :merge:`791`). By `Kyle Brindley`_.

******************
0.8.0 (2024-03-29)
******************

Breaking changes
================
- Remove the deprecated public ``generate`` method of the parameter generators. Parameter studies are generated on class
  instantiation since version :ref:`0.6.1` (:issue:`605`, :merge:`777`). By `Kyle Brindley`_.
- Remove the deprecated ``builders`` module. Replaced by ``scons_extensions`` since version :ref:`0.7.1` (:issue:`511`,
  :merge:`778`). By `Kyle Brindley`_.
- Remove the deprecated ``<name>_program`` builders' keyword arguments. Replaced by ``program`` since version
  :ref:`0.7.1` (:issue:`508`, :merge:`779`). By `Kyle Brindley`_.
- Remove unused Abaqus Python parsers to reduce maintenance overhead (:issue:`614`, :merge:`780`). By `Kyle Brindley`_.
- Remove the ``waves quickstart`` subcommand in favor of the more general purpose ``waves fetch`` subcommand. Older
  behavior can be identically reproduced as ``waves fetch modsim_template``. The intention is to add additional template
  projects and disambiguate the various "quickstart" tutorials as distinct from the template project(s) (:issue:`604`,
  :merge:`788`). By `Kyle Brindley`_.

Documentation
=============
- Simplify the Cubit tutorial SConscript interfaces (:issue:`618`, :merge:`771`). By `Kyle Brindley`_.
- Add draft outline for a sensitivity study tutorial (:issue:`619`, :merge:`774`). By `Kyle Brindley`_.
- Remove unnecessary str conversions in tutorial SCons configuration files. No longer necessary in SCons>=4.6
  (:issue:`612`, :merge:`776`). By `Kyle Brindley`_.
- Add a reference section to the multi-action task tutorial (:issue:`623`, :merge:`782`). By `Kyle Brindley`_.
- Add a references section to the native SCons quickstart tutorial (:issue:`622`, :merge:`783`). By `Kyle Brindley`_.
- Complete the refernces section of the post-processing tutorial and add a brief discussion about the purpose of the
  generator expression (:issue:`573`, :merge:`786`). By `Kyle Brindley`_.
- Address the CEA-TEC edits in the computational practices discussion (:issue:`629`, :merge:`787`). By `Kyle Brindley`_.

Internal Changes
================
- Standardize tutorial multiline and hanging indents (:issue:`613`, :merge:`769`). By `Sergio Cordova`_.
- Fetch each tutorial to a unique temporary directory before running as a system test. Avoids race conditions on the
  tutorial sconsign database file during system tests (:issue:`620`, :merge:`775`). By `Kyle Brindley`_.
- Improve private/public marking in ``help()`` and provide cleaner package/module namespaces for greater consistency
  with other Python packages in the scientific computing stack (:issue:`624`, :merge:`781`). By `Kyle Brindley`_.
- Standardize internal API/CLI design around raised exceptions and CLI conversion of known exceptions to error messages
  and non-zero exit codes (:issue:`621`, :merge:`784`). By `Kyle Brindley`_.
- Add CLI sign-of-life tests with help/usage to the system tests in the regression suite (:issue:`627`, :merge:`785`).
  By `Kyle Brindley`_.
- Unpacking iterables in the ``typing.Literal`` interface doesn't work in Python 3.10. Hardcode the literal type hints
  for now (:issue:`630`, :merge:`789`). By `Kyle Brindley`_.
- Include the numbered tutorial fetch command in the core tutorial system tests (:issue:`625`, :merge:`790`). By `Kyle
  Brindley`_.

Enhancements
============
- Simplify core tutorial waves fetch commands (:issue:`617`, :merge:`773`). By `Sergio Cordova`_.

.. _0.7.10:

*******************
0.7.10 (2024-03-15)
*******************

New Features
============
- Public API function for building WAVES-like actions that change to the build directory before running a shell command
  (:issue:`611`, :merge:`759`). By `Kyle Brindley`_.
- Add unit and regression testing to the modsim template (:issue:`603`, :merge:`760`). By `Kyle Brindley`_.

Bug fixes
=========
- Fix issue in odb_extract to handle case where elemental and nodal data is present in the same field output
  (:issue:`601`, :merge:`742`). By `Prabhu Khalsa`_.
- Allowing merging of previous parameter studies with a single parameter set (:issue:`565`, :merge:`763`). By `Kyle
  Brindley`_.

Documentation
=============
- Add the odb extract HDF5 file structure discussion to the CLI and builder (:issue:`563`, :merge:`744`). By `Prabhu
  Khalsa`_.
- Add the post-processing tutorial image example and discuss the purpose of catenating the simulation results with the
  parameter study object (:issue:`574`, :merge:`747`). By `Kyle Brindley`_.
- Add odb extract structure and relationship to Xarray, h5py, HDF Group tools to tutorial 08 about data extraction
  (:issue:`572`, :merge:`748`). By `Kyle Brindley`_.
- Replace docstring types with type annotations for future static type checking (:merge:`749`). By `Kyle Brindley`_.
- Replace f-strings with scons template substitution in escape sequences tutorial (:issue:`587`, :merge:`726`).
  By `Sergio Cordova`_ and `Kyle Brindley`_.
- Added unit test tutorial (:issue:`302`, :merge:`724`). By `Sergio Cordova`_.
- Add additional discussion about Python programming and the Python script builder to the post-processing tutorial
  (:issue:`106`, :merge:`752`). By `Kyle Brindley`_.
- Updated ``waves fetch`` command to facilitate starting from any tutorial (:issue:`606`, :merge:`753`).
  By `Sergio Cordova`_.
- Add SCons workflow debugging tips to the modsim template README and HTML documentation (:issue:`525`, :merge:`756`).
  By `Kyle Brindley`_.
- Moved unit test tutorial to core lessons as the new tutorial 10 (:issue:`602`, :merge:`751`). By `Sergio Cordova`_.
- Use parameter set functions for better simulation variable documentation in the tutorials and modsim template
  (:issue:`474`, :merge:`764`). By `Kyle Brindley`_.
- Use the SCons 4.6.0 feature to limit project usage to project-specific options and variables in the tutorials
  (:issue:`591`, :merge:`765`). By `Kyle Brindley`_.
- Use the more generic 'modsim' term instead of the group specific 'EABM' (:issue:`615`, :merge:`766`). By `Kyle
  Brindley`_.
- Flesh out regression testing tutorial discussion (:issue:`464`, :merge:`767`). By `Kyle Brindley`_.

Internal Changes
================
- Add a linting package to the CI environment (:issue:`607`, :merge:`754`). By `Kyle Brindley`_.
- Add a linting CI job to the test suite (:issue:`608`, :merge:`755`). By `Kyle Brindley`_.
- Use the full Abaqus Python session object namespace to clarify relationship to imports (:issue:`609`, :merge:`757`).
  By `Kyle Brindley`_.
- Update the correlation coefficients draft script with changes from the post-processing tutorial (:issue:`610`,
  :merge:`758`). By `Kyle Brindley`_.
- Use the public API function for builder action prefixes that change to the build directory before running a shell
  command (:issue:`611`, :merge:`759`). By `Kyle Brindley`_.

Enhancements
============
- Stream the wrapped scons command STDOUT from the waves build subcommand (:merge:`745`). By `Kyle Brindley`_.
- Submit all targets simultaneously in the waves build subcommand (:merge:`745`). By `Kyle Brindley`_.
- Build the Conda environment artifact to the build directoy in the modsim template (:merge:`761`). By `Kyle Brindley`_.
- Use pathlib objects in the modsim template and reduce str conversions which are no longer necessary in SCons 4.6.0
  (:merge:`762`). By `Kyle Brindley`_.

******************
0.7.9 (2024-02-22)
******************

Bug fixes
=========
- waves visualize now works with an input file even if an SConstruct file does not exist (:issue:`586`, :merge:`725`).
  By `Prabhu Khalsa`_.
- Fix bug in abaqus_file_parser that manifests when there is just one line of data in the field output section of the
  csv file (:issue:`599`, :merge:`740`). By `Prabhu Khalsa`_.

Documentation
=============
- Update the hardcoded copyright dates in the README and LICENSE files. By `Kyle Brindley`_.
- Fix some typos in tutorial 01 and edit sentence for clarity (:issue:`592`, :merge:`730`). By `Prabhu Khalsa`_.
- Fixed issue where class level api documentation were not being populated correctly (:issue:`595`, :merge:`733`).
  By `Sergio Cordova`_.

Internal Changes
================
- Explicit include of the tutorial and modsim template directories to help the conda-forge build find the non-Python
  files (:issue:`589`, :merge:`728`). By `Kyle Brindley`_.
- Silence irrelevant warning thrown by XArray (:issue:`590`, :merge:`729`). By `Kyle Brindley`_.
- Add boa to the CI environment for faster packaging (:issue:`593`, :merge:`731`). By `Kyle Brindley`_.
- Build with boa/mambabuild for faster packaging and run CI test jobs in parallel (:issue:`594`, :merge:`732`). By `Kyle
  Brindley`_.
- Remove duplicate logic in CI environment creation (:issue:`8`, :merge:`734`). By `Kyle Brindley`_.
- Remove ``dev`` branch and begin using a single production ``main`` branch (:issue:`597`, :merge:`737`). By `Kyle
  Brindley`_.
- Place pytest results in a build directory to avoid cluttering the source directory (:issue:`598`, :merge:`741`). By
  `Kyle Brindley`_.

******************
0.7.8 (2024-01-16)
******************

New Features
============
- Add no_labels option to waves visualize (:issue:`583`, :merge:`717`). By `Prabhu Khalsa`_.
- New print-tree feature in waves visualize (:issue:`582`, :merge:`718`). By `Prabhu Khalsa`_.
- Add input-file option to waves visualize to graph provided input (:issue:`584`, :merge:`719`). By `Prabhu Khalsa`_.

Bug fixes
=========
- Handle redirected output target file substitution during ssh wrapped builders (:issue:`580`, :merge:`715`).
  By `Sergio Cordova`_.

Documentation
=============
- Remove waves module testing instructions from waves-eamb documentation (:issue:`581`, :merge:`716`).
  By `Sergio Cordova`_.
- Updated keywords in build system discussion for make (:issue:`585`, :merge:`720`). By `Sergio Cordova`_.

******************
0.7.7 (2023-12-18)
******************

Internal Changes
================
- Update package structure discovery during the conda-build (:merge:`712`). By `Kyle Brindley`_.

******************
0.7.6 (2023-12-11)
******************

New Features
============
- Prototype Sphinx builders (:issue:`564`, :merge:`701`). By `Kyle Brindley`_.

Bug fixes
=========
- Fix abaqus_file_parser to handle case where history region data appears immediately after step
  metadata (:issue:`576`, :merge:`705`). By `Prabhu Khalsa`_.

Documentation
=============
- Add PEP-8 reference and citation to the first two tutorials (:issue:`524`, :merge:`688`). By `Kyle Brindley`_.
- Add the project badges to the HTML docs landing page (:issue:`422`, :merge:`689`). By `Kyle Brindley`_.
- Update version control discussion to compare with product data management and add VCS references (:issue:`484`,
  :merge:`690`). By `Kyle Brindley`_.
- Add SCons construction environment discussion to the compute environment management section (:issue:`522`,
  :merge:`691`). By `Kyle Brindley`_.
- Draft discussion about data archival (:issue:`467`, :merge:`692`). By `Kyle Brindley`_.
- Cite and briefly discuss the role of standards documents from ASME and NASA (:issue:`483`, :merge:`693`). By `Kyle
  Brindley`_.
- Remove out-of-date AEA Quinoa tutorial warning. By `Kyle Brindley`_.
- Simplified multi-action task tutorial (:issue:`553`, :merge:`695`). By `Sergio Cordova`_.
- Added consistent tutorial directories (:issue:`562`, :merge:`699`). By `Sergio Cordova`_.
- Added Abaqus part image script and images to the modsim_template (:issue:`423`, :merge:`700`). By `Sergio Cordova`_.
- Add a brief abstract/'Why WAVES?' purpose statement to the documentation (:issue:`548`, :merge:`704`). By `Kyle
  Brindley`_.
- Update modsim template to use SCons variable substitution (:issue:`579`, :merge:`714`). By `Sergio Cordova`_.

Internal Changes
================
- Require exact exceptions during unit testing of error handling (:issue:`568`, :merge:`706`). By `Sergio Cordova`_.
- Call system exit and associated error message more directly (:issue:`566`, :merge:`708`). By `Sergio Cordova`_.
- Reduce permissions of micro version bumping automation (:issue:`578`, :merge:`709`). By `Kyle Brindley`_.

Enhancements
============
- Default to required task-by-task keyword arguments in the SSH builder to allow tasks to use unique remote directories,
  e.g. during parameter studies (:issue:`560`, :merge:`694`). By `Kyle Brindley`_.
- More robust user provided stdout file handling and allow multiple targets with the same file stem (:issue:`556`,
  :merge:`696`). By `Kyle Brindley`_.
- More robust search for Cubit bin for variations on the executable relationship to bin and MacOS installation directory
  names (:issue:`569`, :merge:`702`). By `Kyle Brindley`_.
- Default to local project help message and an override option in ``waves.scons_extensions.project_help_message`` taking
  advantage of an SCons 4.6.0 ``env.Help()`` keyword argument update. Backward compatibility with older versions of
  SCons is preserved (:issue:`571`, :merge:`703`). By `Kyle Brindley`_.
- Find all ``INPUT=`` parameter file dependencies in the Abaqus implicit DEPEndency scanner (:issue:`577`,
  :merge:`707`). By `Matthew Fister`_.

******************
0.7.5 (2023-10-27)
******************

New Features
============
- Add experimental builder support for Quinoa (:issue:`550`, :merge:`676`). By `Kyle Brindley`_.

Documentation
=============
- Add work-in-progress tutorial for Quinoa with example problem provided by `Christopher Long`_ (:issue:`550`,
  :merge:`676`). By `Kyle Brindley`_.

Internal Changes
================
- Add quinoa tutorial's local AEA server build to the regression suite (:issue:`554`, :merge:`683`). By `Kyle
  Brindley`_.
- Move tutorial and modsim template files into the package repository for reduced special handling during packaging
  (:merge:`684`). By `Kyle Brindley`_.
- Merge remaining shell system tests to pytest managed execution (:merge:`684`). By `Kyle Brindley`_.

******************
0.7.4 (2023-10-26)
******************

Bug fixes
=========
- Handle indexed SCons source strings in the SSH build wrapper (:merge:`679`). By `Kyle Brindley`_.

Documentation
=============
- Add the PDF documentation cover as the EPUB cover (:merge:`672`). By `Kyle Brindley`_.
- Simplified scons quickstart ``SConscript`` file (:issue:`521`, :merge:`675`). By `Sergio Cordova`_.
- Change the modsim template name from ``quickstart`` to ``modsim_template`` to avoid confusion with the quickstart
  tutorials. Add a short discussion about retrieving the modsim template files (:issue:`552`, :merge:`678`). By `Kyle
  Brindley`_.

Internal Changes
================
- Reduce code duplication in documentation build configuration (:merge:`671`). By `Kyle Brindley`_.
- The EPUB cover handling requires the imagemagick package, so use a ``regression`` alias to exclude the EPUB build from
  the regression suite until we decide how to handle the unavailability of imagemagick for Windows or accept linux/macos
  only CI builds (:merge:`672`). By `Kyle Brindley`_.
- Refine a sphinx build prototype builder and interface. By `Kyle Brindley`_.
- Handle spaces in paths for ``odb_extract`` (:issue:`549`, :merge:`674`). By `Sergio Cordova`_.
- Use dictionary unpacking to place parameter sets in task definitions (:merge:`677`). By `Kyle Brindley`_.

Enhancements
============
- Add loud failures to Abaqus Python CLI errors (:issue:`551`, :merge:`679`). By `Sergio Cordova`_.

******************
0.7.3 (2023-10-17)
******************

New Features
============
- Add a function for printing build failure STDOUT files. Aids in project system testing the tutorials, but can also be
  useful for end users to print the failed task's STDOUT live during workflow execution (:issue:`546`, :merge:`665`). By
  `Kyle Brindley`_ and `Matthew Fister`_.

Documentation
=============
- Updated tutorials to use ``waves fetch`` to facilitate starting from any tutorial (:issue:`466`, :merge:`631`).
  By `Sergio Cordova`_.
- Add favicon image for HTML documentation build (:issue:`547`, :merge:`666`). By `Kyle Brindley`_.
- Updated release instructions to use git tag (:issue:`532`, :merge:`667`). By `Sergio Cordova`_.

Internal Changes
================
- Remove the tutorials' journal file short options. In practice, they frequently conflict with the Abaqus command
  options and cause difficult to debug error message. Long options are less likely to produce this behavior
  (:issue:`542`, :merge:`661`). By `Kyle Brindley`_.
- Fixed failing tests (:issue:`544`, :merge:`663`, :issue:`545`, :merge:`664`). By `Sergio Cordova`_.

******************
0.7.2 (2023-10-10)
******************

New Features
============
- Added draft Sphinx dependency scanner (:merge:`640`). By `Kyle Brindley`_.
- Add an SCons environment constructor from shell commands (:issue:`531`, :merge:`646`). By `Kyle Brindley`_.
- Add wrapper function and decorator to catenate builder actions and wrap with an outer program (:merge:`647`,
  :merge:`648`). By `Kyle Brindley`_.
- Abaqus solver, Abaqus journal, and Sierra SLURM Sbatch builders (:merge:`647`, :merge:`648`). By `Kyle Brindley`_.
- Draft SSH builder wrapper (:merge:`649`). By `Kyle Brindley`_.
- Python SLURM Sbatch builder (:issue:`539`, :merge:`657`). By `Kyle Brindley`_.
- Accept Sbatch command-line options in the Sbatch wrapper builders (:issue:`539`, :merge:`657`). By `Kyle Brindley`_.

Documentation
=============
- Fixed broken AEA Compute Environment documentation links (:issue:`527`, :merge:`643`). By `Sergio Cordova`_.
- Use the Abaqus solver SLURM Sbatch builder in the associated tutorial (:merge:`647`). By `Kyle Brindley`_.
- Use the draft SSH builder wrapper in the remote execution tutorial (:merge:`649`). By `Kyle Brindley`_.
- Update the builder SConstruct examples (:issue:`534`, :merge:`653`). By `Kyle Brindley`_.
- Add a version check warning and instructions to the quickstart and core tutorials (:issue:`540`, :merge:`656`). By
  `Kyle Brindley`_.

Internal Changes
================
- Trial update to run the system test suite in parallel. It's possible the system tests are not yet thread safe (using a
  common ``.sconsign.dblite`` file but separate build directories), but this wasn't observed in local testing. It's also
  possible that Abaqus token availability will periodically timeout job submissions. If this produces many false negative
  tests requiring manual intervention, revert commit ``d2e3c9d1``  (:issue:`519`, :merge:`641`). By `Kyle Brindley`_.
- Elevate PDF documentation build warnings to errors to match other sphinx build behaviors (:merge:`642`). By `Kyle
  Brindley`_.
- Reduce operations required to set the builder post actions (:issue:`535`, :merge:`650`). By `Kyle Brindley`_.
- More complete tests for the ssh builder action wrapper function (:issue:`533`, :merge:`651`). By `Kyle Brindley`_.
- Common function for returning a builder's actions as a list of string (:issue:`537`, :merge:`652`). By `Kyle
  Brindley`_.
- Update package build requirements to reflect current working package combinations. Eventually we will need to solve
  the ``setuptools_scm>=8`` error messages (:issue:`538`, :merge:`655`). By `Kyle Brindley`_.

Enhancements
============
- In the SLURM ``sbatch`` builder, use the ``sbatch`` native output redirection to capture the executing job's output
  instead of the minimal ``sbatch`` output (:issue:`528`, :merge:`644`). By `Kyle Brindley`_.
- Use the draft Sphinx dependency scanner in the quickstart template modsim project (:issue:`529`, :merge:`645`). By
  `Kyle Brindley`_.
- Update the Sierra execution environment solution (:issue:`531`, :merge:`646`). By `Kyle Brindley`_.

.. _0.7.1:

******************
0.7.1 (2023-08-28)
******************

Bug fixes
=========
- Fix odb_extract to ensure 'mode=csv' when odbreport is called. (:issue:`517`, :merge:`630`). By `Prabhu Khalsa`_.

Breaking changes
================
- Deprecate the too-general ``parameter_study <study type>`` command-line utility name in favor of ``waves <study
  type>`` to avoid utility conflicts with other packages (:issue:`494`, :merge:`612`). By `Kyle Brindley`_.
- Standardize the builder program path keyword from ``<thing>_program`` to ``program`` for greater consistency in
  builder APIs. The older keywords are preseved for backward compatibility, but they raise a deprecation warning
  (:issue:`495`, :merge:`613`). By `Kyle Brindley`_.
- Rename the ``waves.builders`` module as ``waves.scons_extensions`` to reflect the growing scope of SCons extensions
  beyond a collection of builders. Backward compatilibity is maintained by duplicating the module under the old name
  with a deprecation warning (:issue:`492`, :merge:`618`, :issue:`512`, :merge:`621`, :merge:`627`, :merge:`628`). By
  `Kyle Brindley`_.

New Features
============
- Add experimental builder support for Sierra (:issue:`500`, :merge:`622`). By `Kyle Brindley`_.
- Add vertical option to waves visualize (:issue:`514`, :merge:`624`). By `Prabhu Khalsa`_.

Documentation
=============
- Update the tutorial and template modsim model name to reflect the geometry instead of the mesh (:issue:`461`,
  :merge:`614`, :merge:`615`). By `Kyle Brindley`_.
- Trim down the README to focus on end users. Move developer notes directly into the HTML developer manual
  (:issue:`505`, :merge:`616`). By `Kyle Brindley`_.
- Add the WAVES primarymark image to the PDF title page (:merge:`620`). By `Kyle Brindley`_.
- Update the Cubit tutorial to demonstrate a side-by-side comparison of Abaqus and Sierra, where the Cubit tasks are
  reused for both solver workflows (:issue:`513`, :merge:`623`). By `Kyle Brindley`_.
- Simplified quickstart ``SConscript`` file (:issue:`453`, :merge:`619`). By `Sergio Cordova`_.

Internal Changes
================
- Reduce the runtime dependency from the full matplotlib to matplotlib-base following the conda-forge recommendation:
  https://conda-forge.org/docs/maintainer/knowledge_base.html#matplotlib (:issue:`440`, :merge:`611`). By `Kyle
  Brindley`_.
- Explore a draft correlation coefficients post-procesing tutorial (:merge:`615`). By `Kyle Brindley`_.
- Update to use Abaqus 2023 (:issue:`509`, :merge:`617`). By `Kyle Brindley`_.
- More complete clean behavior for the documentation targets to reduce dev/main source conflicts during Gitlab-Pages
  builds (:issue:`516`, :merge:`625`, :merge:`626`). By `Kyle Brindley`_.
- Update the expected Cubit version from 16.04 to 16.12 (:issue:`510`, :merge:`634`). By `Sergio Cordova`_.
- Add the ``--build-dir`` command-line option to the quickstart tutorials to enable the system tests to run in
  non-default, temporary build directories (:issue:`518`, :merge:`635`). By `Kyle Brindley`_.
- Drive the system tests (tutorials) from pytest during conda builds (:merge:`629`). By `Kyle Brindley`_.
- Upgrade to Anaocnda 2023 on Gitlab-CI environment (:issue:`520`, :merge:`636`). By `Sergio Cordova`_.
- Return to the conda build command (:merge:`637`). By `Kyle Brindley`_.
- Handle parameter study script input outside of argparse (:issue:`72`, :merge:`633`). By `Sergio Cordova`_.
- Removed debug argument from CLI (:issue:`76`, :merge:`632`). By `Sergio Cordova`_.

*******************
0.6.21 (2023-07-21)
*******************

New Features
============
- Added Abaqus input dependency scanner (:issue:`444`, :merge:`602`). By `Sergio Cordova`_.

Documentation
=============
- Add the waves visualize image to the geometry tutorial (:issue:`486`, :merge:`603`). By `Kyle Brindley`_.
- Add the waves visualize image to the partition and mesh tutorial (:issue:`502`, :merge:`606`). By `Kyle Brindley`_.
- Add waves visualize image and directed graph discussion to all core tutorials (:issue:`504`, :merge:`607`). By `Kyle
  Brindley`_.

Enhancement
===========
- Add option to adjust font size in ``waves visualize`` sub-command (:issue:`501`, :merge:`604`). By `Kyle Brindley`_.

Internal Changes
================
- Add pytest-cov to CI environment (:merge:`599`). By `Kyle Brindley`_.
- Add coverage report to internal CI jobs (:issue:`496`, :merge:`600`). By `Kyle Brindley`_.
- Drive the system tests (tutorials) from SCons and pytest (:merge:`601`). By `Kyle Brindley`_.
- Add an optional epub documentation build (:merge:`605`). By `Kyle Brindley`_.

*******************
0.6.20 (2023-06-29)
*******************

Documentation
=============
- Removed semaphore files in tutorials (:issue:`488`, :merge:`591`). By `Sergio Cordova`_
- Updated parameter study CLI messages to reflect yaml file behavior changes (:issue:`490`, :merge:`593`). By `Sergio
  Cordova`_
- Clarify the difference between the ``copy_substitute`` function and the WAVES-SCons builders. Update missing interface
  descriptions and return value descriptions (:issue:`493`, :merge:`595`). By `Kyle Brindley`_.

Enhancement
===========
- Overwrite h5 files if content changed on parameter generators (:issue:`441`, :merge:`590`). By `Sergio Cordova`_
- Overwrite yaml files if content changed on parameter generators (:issue:`487`, :merge:`592`). By `Sergio Cordova`_

Internal Changes
================
- Remove unused environment variables from Conda package recipe (:issue:`480`, :merge:`587`). By `Kyle Brindley`_.
- Avoid packaging Sphinx intermediate build files during documentation packaging (:issue:`481`, :merge:`588`). By `Kyle
  Brindley`_.
- Use the conda-forge recommended 'python-build' package instead of 'build', which is apparently deprecated as too
  general a name (:issue:`481`, :merge:`589`). By `Kyle Brindley`_.
- Updated h5 and yaml parameter generator tests to use the same data input (:issue:`491`, :merge:`594`). By `Sergio
  Cordova`_

*******************
0.6.19 (2023-06-14)
*******************

Bug fixes
=========
- Check if 'frames' and 'historyRegions' keys exist before using them. Fixing bug from :merge:`574`
  (:issue:`479`, :merge:`584`). By `Prabhu Khalsa`_.

Internal Changes
================
- Migrate from ``setup.py`` builds to the ``build`` package (:issue:`477`, :merge:`582`). By `Kyle Brindley`_.
- Make the ``odb_extract`` builder more OS portable (:merge:`583`). By `Kyle Brindley`_.
- Refactored ``test_merge`` functions in unit tests (:issue:`387`, :merge:`575`). By `Sergio Cordova`_.

*******************
0.6.18 (2023-06-09)
*******************

Internal Changes
================
- Improve GitHub release workflow to match recommended practice (:merge:`580`). By `Kyle Brindley`_.

*******************
0.6.17 (2023-06-09)
*******************

Bug fixes
=========
- Fix other missing dimensions of history output dataset when step data is missing (:issue:`470`, :merge:`570`).
  By `Prabhu Khalsa`_.
- Fix field output dimensions when step data is missing (:issue:`473`, :merge:`574`). By `Prabhu Khalsa`_.
- Update numpy.float to numpy.float64 in abaqus_file_parser.py (:issue:`476`, :merge:`577`). By `Prabhu Khalsa`_.

Documentation
=============
- Complete the discussion sections in the data archival tutorial (:issue:`465`, :merge:`571`). By `Kyle Brindley`_.
- Minor changes in tutorials that ensure expected behavior when using the copy button (:issue:`471`, :merge:`573`).
  By `Sergio Cordova`_.

Enhancements
============
- Sort the ``fetch`` available files output (:issue:`475`, :merge:`576`). By `Kyle Brindley`_.

*******************
0.6.16 (2023-05-15)
*******************

Bug fixes
=========
- Fix missing dimension of history output dataset when step data is missing (:issue:`468`, :merge:`565`).
  By `Prabhu Khalsa`_.

Documentation
=============
- Update citations to version 0.6.15 and associated DOI (:issue:`460`, :merge:`561`). By `Kyle Brindley`_.

Internal Changes
================
- Upgrade to Anaconda 2021 on Gitlab-CI environment (:issue:`463`, :merge:`563`).
- Remove Gitlab-CI workarounds from the CI configuration (:issue:`469`, :merge:`566`). By `Kyle Brindley`_.
- Prevent creation of pycache files during documentation and pytest tasks (:issue:`34`, :merge:`567`). By `Kyle
  Brindley`_.

Enhancements
============
- Return executable paths with double quotes around parts containing spaces. Should make executing commands by absolute
  path in Windows command prompt and powershell more robust (:issue:`462`, :merge:`562`). By `Kyle Brindley`_.

*******************
0.6.15 (2023-05-04)
*******************

Documentation
=============
- Linked argparse tutorial in tutorial 01 (:issue:`439`, :merge:`549`). By `Sergio Cordova`_.
- Removed datacheck from the quickstart tutorials (:issue:`446`, :merge:`551`). By `Sergio Cordova`_.
- Hardcoded the source and target lists in the quickstart tutorials (:issue:`448`, :merge:`552`). By `Sergio Cordova`_.
- Standardize the discussion of builder specific keyword arguments (:issue:`459`, :merge:`558`). By `Kyle Brindley`_.
- Add an option to skip Tutorial 00: SConstruct with the waves fetch command (:issue:`451`, :merge:`559`). By `Kyle
  Brindley`_.

Internal Changes
================
- Fix the license syntax in ``CITATION.cff`` to help Zenodo recognize the license type (:merge:`546`). By `Kyle
  Brindley`_.
- Cleaned up conda package CI files after ``conda build`` (:issue:`442`, :merge:`547`). By `Sergio Cordova`_.
- Removed mutable default arguments from python scripts (:issue:`454`, :merge:`553`). By `Sergio Cordova`_.

Enhancements
============
- Added ``--exclude-regex`` argument to ``visualize`` subcommand (:issue:`419`, :merge:`548`). By `Sergio Cordova`_.
- Added abaqus explicit and standard emitters to ``AbaqusSolver`` (:issue:`443`, :merge:`554`). By `Sergio Cordova`_.
- Add Matlab script parent directory to Matlab path in the Matlab script builder action. No longer necessary to copy
  Matlab script(s) to build directory prior to execution. Matlab script copy operation no longer performed by default.
  Builder still considered "experimental" until a tutorial is released (:issue:`456`, :merge:`555`). By `Kyle
  Brindley`_.
- Add an example Matlab input parser to the Matlab tutorial script (:issue:`420`, :merge:`556`). By `Kyle Brindley`_.
- Add an example Matlab docstring in the sphinxcontrib-matlabdomain style (:issue:`457`, :merge:`557`). By `Kyle
  Brindley`_.
- Add an option to override the Abaqus solver builder's emitted targets (:issue:`459`, :merge:`558`). By `Kyle
  Brindley`_.

*******************
0.6.14 (2023-03-23)
*******************

Documentation
=============
- Added ``sphinx-copybutton`` to HTML documentation code blocks (:issue:`415`, :merge:`515`). By `Sergio Cordova`_.
- Add discussion about reproducibility and uniqueness to the LatinHypercube tutorial (:issue:`241`, :merge:`540`). By
  `Kyle Brindley`_.
- Condense the API and CLI sections into the user manual TOC tree (:issue:`241`, :merge:`540`). By `Kyle Brindley`_.

Internal Changes
================
- Fix test for msg_parse.py to achieve 100 percent coverage (:issue:`433`, :merge:`531`). By `Prabhu Khalsa`_.
- Fix test for sta_parse.py to achieve 100 percent coverage (:issue:`435`, :merge:`533`). By `Prabhu Khalsa`_.
- Added ``sphinx-copybutton`` package to environment via pip (:issue:`436`, :merge:`532`). By `Sergio Cordova`_.
- Added ``sphinx-copybutton`` package to environment via conda-forge (:issue:`437`, :merge:`537`). By `Sergio Cordova`_.
- Remove unecessary ``LD_LIBRARY_PATH`` operations in Gitlab-CI configuration (:issue:`438`, :merge:`538`). By `Kyle
  Brindley`_.
- Add waves subcommand sign-of-life tests to the external/GitHub conda-build recipe tests (:issue:`430`, :merge:`539`).
  By `Kyle Brindley`_.
- Seed the LatinHypercube tutorial parameter study (:issue:`241`, :merge:`540`). By `Kyle Brindley`_.
- Fix test execution and assertions for the parameter study command-line utility (:merge:`543`). By `Kyle Brindley`_.
- Fix test for test_odb_extract.py to achieve 100 percent coverage (:issue:`434`, :merge:`534`). By `Prabhu Khalsa`_.

*******************
0.6.13 (2023-03-07)
*******************

New Features
============
- Add a ``waves fetch`` subcommand to fetch bundled modsim template files (:issue:`428`, :merge:`522`). By `Kyle
  Brindley`_.
- Bundle the tutorial files in the conda package (:issue:`427`, :merge:`523`). By `Kyle Brindley`_.

Bug fixes
=========
- Fix issue in excluding nodes of waves visualization (:issue:`426`, :merge:`519`). By `Prabhu Khalsa`_.

Documentation
=============
- Added ORCiD (:issue:`424`, :merge:`517`). By `Scott Ouellette`_
- Add GitHub Pages and Release badges and update conda-forge badge to use shield.io style (:issue:`425`, :merge:`518`).
  By `Kyle Brindley`_.
- Replace ``git archive`` commands with ``waves fetch`` when retrieving source files in the tutorials (:issue:`429`,
  :merge:`525`). By `Kyle Brindley`_.

Internal Changes
================
- Added ``sphinx-copybutton`` package to environment (:issue:`414`, :merge:`516`). By `Sergio Cordova`_.
- Split quickstart copy operations into smaller functions for unit testing (:issue:`428`, :merge:`522`). By `Kyle
  Brindley`_.
- Rename command-line utility module to avoid namespace confusion (:issue:`428`, :merge:`522`). By `Kyle Brindley`_.
- Reduce fetch unit test logic duplication (:issue:`432`, :merge:`527`). By `Kyle Brindley`_.

Enhancements
============
- ``quickstart`` subcommand will create all non-conflicting destination files instead of exiting with an error when
  ``overwrite`` is ``False`` (:issue:`413`, :merge:`520`). By `Kyle Brindley`_.
- ``quickstart`` subcommand will avoid unnecessary file I/O when source and destination file contents match and
  ``overwrite`` is ``True`` (:issue:`413`, :merge:`520`). By `Kyle Brindley`_.
- Add a ``pathlib.Path.rglob`` recursive search to ``waves fetch`` to enable pattern matching on relative paths and
  files (:issue:`431`, :merge:`526`). By `Kyle Brindley`_.

*******************
0.6.12 (2023-02-21)
*******************

New Features
============
- Add alpha release of new visualization feature (:issue:`408`, :merge:`500`). By `Prabhu Khalsa`_.

Documentation
=============
- Update highlighted, non-boilerplate code in the Geometry tutorial (:issue:`410`, :merge:`503`). By `Kyle Brindley`_.
- Clarify the difference between a builder and the ``copy_substitute`` method (:issue:`411`, :merge:`504`). By `Kyle
  Brindley`_.
- Prefer SCons variable substitution over f-strings where possible (:merge:`502`). By `Kyle Brindley`_.
- Miscellaneous clarifications and updates to the tutorials (:issue:`409`, :merge:`505`). By `Kyle Brindley`_.
- Add additional author ORCIDs to the citation file (:issue:`407`, :merge:`512`). By `Kyle Brindley`_.
- Match journal file CLI usage message to the executable/interpretter (:issue:`421`, :merge:`514`). By `Kyle Brindley`_.

Internal Changes
================
- Add networkx to WAVES environment for new visualization feature (:issue:`412`, :merge:`501`). By `Prabhu Khalsa`_.
- Fall back to system anaconda shared environment when project CI environment doesn't exist (:issue:`417`,
  :merge:`511`). By `Kyle Brindley`_.
- Update the minimum scipy version runtime requirement to support the scipy Sobol generator. This change was already
  implemented for the conda-forge and GitHub packages. Change affects AEA Conda channel. (:issue:`278`, :merge:`506`).
  By `Kyle Brindley`_.

Enhancements
============
- Check beginning and end of strings in ``visualize --exclude-list`` to enable excluding by file extension
  (:issue:`418`, :merge:`510`). By `Kyle Brindley`_.

*******************
0.6.11 (2023-01-26)
*******************

Documentation
=============
- Add DOI and conda-forge badges to the README (:issue:`406`, :merge:`496`). By `Kyle Brindley`_.
- Add the GitHub citation file format with Zenodo DOI (:issue:`397`, :merge:`497`). By `Kyle Brindley`_.

*******************
0.6.10 (2023-01-26)
*******************

Documentation
=============
- GitHub recognized BSD 3-Clause license file. Moves the copyright notice to the README (:issue:`404`, :merge:`492`). By
  `Kyle Brindley`_.
- Update installation instructions to reflect conda-forge deployed package (:issue:`405`, :merge:`493`). By `Kyle
  Brindley`_.

Internal Changes
================
- Remove unecessary elements of conda recipes (:merge:`491`). By `Kyle Brindley`_.
- Default to the external/GitHub/conda-forge documentation variant (:issue:`405`, :merge:`493`). By `Kyle Brindley`_.

******************
0.6.9 (2023-01-24)
******************

Internal Changes
================
- Windows friendly test scripts for GitHub conda build recipe (:merge:`488`). By `Kyle Brindley`_.
- Windows friendly unit test path expectations (:issue:`403`, :merge:`489`). By `Kyle Brindley`_.

******************
0.6.8 (2023-01-24)
******************

Internal Changes
================
- Add more meta data to the Conda recipes using the conda-forge example style (:merge:`480`). By `Kyle Brindley`_.
- MacOS friendly cp symlink dereference in conda recipes (:merge:`481`). By `Kyle Brindley`_.
- List modules in setuptools packages configuration (:merge:`482`). By `Kyle Brindley`_.
- Use Python for OS-agnostic documentation packaging in conda build recipes (:merge:`483`). By `Kyle Brindley`_.
- Windows friendly path construction in the Sphinx configuration (:merge:`486`). By `Kyle Brindley`_.

******************
0.6.7 (2023-01-23)
******************

Documentation
=============
- Add package meta data to conda build recipes (:issue:`401`, :merge:`476`). By `Kyle Brindley`_.
- Add PDF documentation to the GitHub release workflow (:issue:`402`, :merge:`477`). By `Kyle Brindley`_.

******************
0.6.6 (2023-01-23)
******************

Documentation
=============
- Expand the instructions for installing from tar archive release (:issue:`399`, :merge:`471`). By `Kyle Brindley`_.

Internal Changes
================
- Update CI minimum dependency versions, specifically ``sphinx_rtd_theme`` to fix the GitHub Pages build (:issue:`398`,
  :merge:`470`). By `Kyle Brindley`_.
- Draft GitHub release workflow (:issue:`399`, :merge:`471`). By `Kyle Brindley`_.
- Build PDF documentation as external audience variation (:issue:`400`, :merge:`472`). By `Kyle Brindley`_.
- Troubleshoot to working release (:merge:`474`). By `Kyle Brindley`_.

******************
0.6.5 (2023-01-20)
******************

Documentation
=============
- Use the GitHub repository URL wherever possible as the officially published repository and documentation. Duplicate
  URLs where necessary (:issue:`393`, :merge:`463`). By `Kyle Brindley`_.

Internal Changes
================
- Add a Conda recipe that bundles the documentation built with external/GitHub URLs (:issue:`392`, :merge:`464`). By
  `Kyle Brindley`_.

******************
0.6.4 (2023-01-20)
******************

Documentation
=============
- Add GitHub.com Pages workflow (:merge:`459`). By `Kyle Brindley`_.

Internal Changes
================
- Fix the man page build/ignore alias (:merge:`458`). By `Kyle Brindley`_.
- Full depth GitHub-Pages checkout to guarantee version tags in the documentation build (:merge:`461`). By `Kyle
  Brindley`_.

******************
0.6.3 (2023-01-20)
******************

Documentation
=============
- Add the BSD-3-Clause license and copyright notice (:issue:`389`, :merge:`452`). By `Kyle Brindley`_.
- Add installation and interim installation (pending conda-forge deployment) instructions. Reduce
  compute-server-specific language. By `Kyle Brindley`_.

Internal Changes
================
- Use a common solution to finding the build subdirectory in all emitters (:issue:`390`, :merge:`453`). By `Kyle
  Brindley`_.

Enhancements
============
- Add a Matlab environment file output to the experimental Matlab script builder and emitter (:issue:`390`,
  :merge:`453`). By `Kyle Brindley`_.

******************
0.6.2 (2023-01-13)
******************

New Features
============
- Add SALib ``fast_sampler`` to the list of tested samplers for parameter generation (:merge:`444`). By `Kyle
  Brindley`_.
- Add SALib ``finite_diff`` to the list of tested samplers (:merge:`447`). By `Kyle Brindley`_.
- Add SALib ``morris`` to the list of tested samplers (:issue:`386`, :merge:`443`). By `Kyle Brindley`_.
- Add an experimental draft builder for Matlab scripts (:issue:`388`, :merge:`449`). By `Kyle Brindley`_.

Documentation
=============
- Adjust PDF documentation build's font size of code-blocks to fit 120 character width files (:merge:`445` :merge:`446`). By `Kyle
  Brindley`_.
- Remove unnecessary nested f-string and SCons variable replacement syntax from post-processing tasks in core tutorials
  (:issue:`377`, :merge:`448`). By `Kyle Brindley`_.

Internal Changes
================
- Reduce builder emitter code duplication with a common "first target" emitter (:issue:`388`, :merge:`449`,
  :merge:`450`). By `Kyle Brindley`_.

.. _0.6.1:

******************
0.6.1 (2023-01-06)
******************

New Features
============
- Add a general SALib sampler parameter generator (:issue:`385`, :merge:`436`). By `Kyle Brindley`_.
- Allow passing of arbitrary keyword arguments to the parameter generator sampling method through the parameter
  generator interface (:issue:`381`, :merge:`440`). By `Kyle Brindley`_.

Internal Changes
================
- Adds salib to the runtime requirements (:issue:`385`, :merge:`436`). By `Kyle Brindley`_.
- Generate the parameter study on parameter generator class instantiation. Preserve the public ``generate()`` method
  with a deprecation warning (:issue:`381`, :merge:`440`). By `Kyle Brindley`_.

*******************
0.5.11 (2023-01-05)
*******************

New Features
============
- Add a parameter-set-as-dictionaries method to the parameter generator class (:issue:`378`, :merge:`430`). By `Kyle
  Brindley`_.
- Add a general scipy sampler parameter generator (:issue:`384`, :merge:`435`). By `Kyle Brindley`_.

Documentation
=============
- Add the parameter study dictionary method to each parameter generator's external API and update the CartesianProduct
  tutorial discussion (:issue:`382`, :merge:`434`). By `Kyle Brindley`_.

Internal Changes
================
- Add seaborn package to the development and CI environments (:issue:`380`, :merge:`432`). By `Kyle Brindley`_.
- Consolidate the scipy based parameter generator logic (:issue:`383`, :merge:`433`). By `Kyle Brindley`_.
- Remove unused variables from tutorial workflow configurations (:issue:`382`, :merge:`434`). By `Kyle Brindley`_.
- Add salib package to the development and CI environments (:merge:`437`). By `Kyle Brindley`_.

Enhancements
============
- Use a YAML file instead of a nested string construction for the post-processing selection dictionary (:issue:`379`,
  :merge:`431`). By `Kyle Brindley`_.

*******************
0.5.10 (2022-12-19)
*******************

New Features
============
- Add configuration files to the archive tutorial and quickstart archival task (:issue:`369`, :merge:`423`). By `Kyle
  Brindley`_.
- Add positive-float input verification to the tutorial and quickstart files (:issue:`375`, :merge:`424`). By `Kyle
  Brindley`_.

Bug fixes
=========
- Fix issue in abaqus_file_parser where first frame of field output didn't get all the dimensions
  (:issue:`376`, :merge:`425`). By `Prabhu Khalsa`_.

Documentation
=============
- Add a supplemental tutorial for input verification using `Argparse type`_ user-defined methods (:issue:`375`,
  :merge:`424`). By `Kyle Brindley`_.

Internal Changes
================
- Account for OS path separator differences in the documentation build for WAVES and the quickstart template files
  (:issue:`4`, :merge:`426`). By `Kyle Brindley`_.

******************
0.5.9 (2022-12-14)
******************

New Features
============
- Add an SCons build function to wrap the parameter generator write method. Removes the need for a user-defined build
  function (:issue:`373`, :merge:`418`). By `Kyle Brindley`_.

Internal Changes
================
- Standardize job name construction throughout tutorials (:issue:`374`, :merge:`420`). By `Kyle Brindley`_.

******************
0.5.8 (2022-12-08)
******************

New Features
============
- Add a Cubit environment modifier helper method (:issue:`367`, :merge:`407`). By `Kyle Brindley`_.
- Manage Cubit environment ``PATH``-like variables from the project configuration file instead of relying on the user
  environment or a project modulefile (:issue:`367`, :merge:`407`). By `Kyle Brindley`_.
- Update the expected Cubit version from 15.8 to 16.04 (:issue:`367`, :merge:`407`). By `Kyle Brindley`_.
- Add a general construction environment ``PATH`` modifier method (:issue:`151`, :merge:`410`). By `Kyle Brindley`_.
- Wrap ``PATH`` modifier and program search into a single method (:issue:`151`, :merge:`410`). By `Kyle Brindley`_.
- Add a WAVES helper method to add default targets text to a project's help message (:issue:`371`, :merge:`413`). By
  `Kyle Brindley`_.
- Add a WAVES helper method to add alias list text to a project's help message (:issue:`370`, :merge:`414`). By `Kyle
  Brindley`_.

Bug fixes
=========
- Fix issue in abaqus_file_parser where coordinates and dimensions didn't match due to history output appearing in
  second step, but not in first (:issue:`372`, :merge:`415`). By `Prabhu Khalsa`_.

Documentation
=============
- Clarify tutorial instructions, edit for grammar and typos, and remove deprecated instructions based on user feedback
  and review (:merge:`412`). By `Kyle Brindley`_.
- Reduce common project configuration boilerplate code in the tutorials and quickstart template files (:issue:`370`,
  :merge:`414`). By `Kyle Brindley`_.

Internal Changes
================
- Remove Matlab and Cubit environment modification from project modulefile (:issue:`367`, :merge:`407`). By `Kyle
  Brindley`_.
- Remove Abaqus environment modification from project modulefile (:issue:`151`, :merge:`410`). By `Kyle Brindley`_.
- Match naming convention for general construction environment ``PATH`` modifier method and Cubit modified method. By
  (:issue:`151`, :merge:`410`) `Kyle Brindley`_.
- Prefer appending over prepending to system ``PATH``. Wrap Cubit environment modifier for behavior consistent with the
  other program search methods (:issue:`368`, :merge:`411`). By `Kyle Brindley`_.

******************
0.5.7 (2022-12-01)
******************

New Features
============
- Add quantitative regression test option to the tutorial and quickstart post-processing script (:issue:`329`,
  :merge:`406`). By `Kyle Brindley`_.

Bug fixes
=========
- Update the ``plot_scatter.py`` tutorial and quickstart post-processing script to account for the new dimension in
  ``odb_extract`` output (:issue:`365`, :merge:`405`). By `Kyle Brindley`_.

Internal Changes
================
- Add builder action unit tests (:issue:`364`, :merge:`404`). By `Kyle Brindley`_.
- Change post-processing script name in the tutorials and quickstart template files to match broader scope
  (:issue:`329`, :merge:`406`). By `Kyle Brindley`_.

******************
0.5.6 (2022-11-29)
******************

New Features
============
- Experimental ``sbatch`` builder and work-in-progress tutorial. Not a final draft with CI regression testing, but a
  starting point to solicit user stories (:issue:`327`, :merge:`398`). By `Kyle Brindley`_.
- Add an archival task tutorial to the core lesson plan (:issue:`351`, :merge:`400`). By `Kyle Brindley`_.
- Add archive task to ``waves quickstart`` template files (:issue:`351`, :merge:`400`). By `Kyle Brindley`_.
- Experimental ``setuptools_scm`` for dynamic version numbering tied to git as a version control system (:issue:`363`,
  :merge:`401`). By `Kyle Brindley`_.

Bug fixes
=========
- Cast the documentation index file Pathlib object to a string to comply with the ``webbrowser.open()`` required
  input variable type (:issue:`362`, :merge:`399`). By `Thomas Roberts`_.

Internal Changes
================
- Remove ``LD_LIBRARY_PATH`` modification from Gitlab-CI modulefile. Modification is used in the AEA shared compute
  environments for c++ user subroutines, but is not necessary for WAVES and interferes with RHEL 7 system libraries
  (:issue:`227`, :merge:`397`). By `Kyle Brindley`_.

******************
0.5.5 (2022-11-23)
******************

Bug fixes
=========
- Add ``__init__.py`` file creation earlier in the tutorials to match the ``PYTHONPATH`` ``SContruct`` changes made in
  :merge:`375` (:issue:`355`, :merge:`383`). By `Kyle Brindley`_.

Documentation
=============
- Add a note about avoiding dependency cycles to the ``copy_substitute`` method (:issue:`338`, :merge:`388`). By `Kyle
  Brindley`_.

Internal Changes
================
- Remove the "short" paper used for external publication. Next external release will be the open source repository
  (:issue:`353`, :merge:`382`). By `Kyle Brindley`_.
- Use keyword arguments in xarray plotting method(s) because positional arguments were deprecated in xarray 2022.11.0:
  https://docs.xarray.dev/en/stable/whats-new.html#deprecations (:issue:`354`, :merge:`385`). By `Kyle Brindley`_.
- Update the preferred Abaqus version to 2022 (:issue:`350`, :merge:`387`). By `Kyle Brindley`_.
- Run Gitlab-CI jobs on either AEA server (:issue:`357`, :merge:`389`). By `Kyle Brindley`_.
- Update the ``odb_extract`` default abaqus executable name convention to match the AEA server installation
  (:issue:`358`, :merge:`390`). By `Kyle Brindley`_.
- Use ``mamba`` for the Gitlab-CI package build process. Testing suggests it will save several minutes (maybe ~10% total
  time) in the ``conda-build`` CI job (:issue:`360`, :merge:`391`). By `Kyle Brindley`_.
- Revert to ``sstelmo`` for deploy jobs until ``aea_service`` account changes are finalized (:merge:`392`). By `Kyle
  Brindley`_.
- Avoid unnecessary job artifact download in Gitlab-CI jobs (:issue:`359`, :merge:`393`). By `Kyle Brindley`_.
- Protect Gitlab-CI deploy type jobs from scheduled pipelines (:issue:`361`, :merge:`394`). By `Kyle Brindley`_.
- No fast-test job on push pipelines to production branches (:merge:`395`). By `Kyle Brindley`_.

******************
0.5.4 (2022-11-07)
******************

Internal Changes
================
- Revert the "short" paper title for external publication. Entire paper build may be removed after final draft
  submission (:issue:`352`:, :merge:`380`). By `Kyle Brindley`_.

******************
0.5.3 (2022-11-02)
******************

New Features
============
- Add the preferred WAVES citation bibtex file to the ``waves quickstart`` template files (:issue:`342`, :merge:`367`).
  By `Kyle Brindley`_.
- Fixed the Sphinx usage of the preferred project citation. Sphinx uses BibTeX, which doesn't have the ``@software``
  style. Added project citations to the quickstart template files (:issue:`343`, :merge:`368`). By `Kyle Brindley`_.

Documentation
=============
- Update the ``CITATION.bib`` file to use the most recent production release number. Update the version release
  instructions to include this step (:issue:`339`, :merge:`366`). By `Kyle Brindley`_.
- Minor typographical fix in API (:issue:`340`, :merge:`369`). By `Kyle Brindley`_.
- Add a work-in-progress tutorial for re-using task definitions (:issue:`63`, :merge:`373`). By `Kyle Brindley`_.
- Add SConscript interface doc strings (:issue:`346`, :merge:`374`). By `Kyle Brindley`_.

Internal Changes
================
- Remove Gitlab-CI developer note that is no longer relevant (:issue:`9`, :merge:`370`). By `Kyle Brindley`_.
- Remove pytest.ini and put settings in pyproject.toml (:issue:`344`, :merge:`371`). By `Prabhu Khalsa`_.
- Standardize on ``pathlib`` constructed absolute paths (:issue:`346`, :merge:`374`). By `Kyle Brindley`_.
- Make all ``PATH``-like modifications once in the project configuration instead of distributed ``sys.path`` calls
  (:issue:`345`, :merge:`375`). By `Kyle Brindley`_.
- Remove unecessary tutorial and quickstart intermediate workflow directories (:issue:`347`, :merge:`376`). By `Kyle
  Brindley`_.

******************
0.5.2 (2022-10-17)
******************

Bug fixes
=========
- Fixed abaqus_file_parser (odb_extract) to correctly parse multiple steps in an odb (:issue:`177`, :merge:`359`). By
  `Prabhu Khalsa`_.
- Added code to abaqus_file_parser (odb_extract) to handle case where odbreport file lists an incorrect number of
  surface sets (:issue:`335`, :merge:`360`). By `Prabhu Khalsa`_.
- Do not append the CSV target when the odb extract builder option is set to delete that file (:issue:`334`,
  :merge:`363`). By `Kyle Brindley`_.

Documentation
=============
- Add draft example for running tasks remotely via SSH (:issue:`316`, :merge:`354`). By `Kyle Brindley`_.
- Match the user manual TOC tree to the tutorials table for less sidebar clutter (:issue:`331`, :merge:`356`). By `Kyle
  Brindley`_.
- Add reference to the ``waves quickstart`` modsim template to the user manual introduction (:issue:`332`,
  :merge:`357`). By `Kyle Brindley`_.
- Reduce man pages to a reference manual for the package API and CLI (:issue:`333`, :merge:`358`). By `Kyle Brindley`_.

Internal Changes
================
- Remove references to the deprecated "amplitudes" file from the tutorials (:issue:`326`, :merge:`355`). By `Kyle
  Brindley`_.
- Add preferred CITATION file to the project root (:issue:`337`, :merge:`362`). By `Kyle Brindley`_.

******************
0.5.1 (2022-09-30)
******************

Breaking changes
================
- Use a more generic name for the builder-global post action argument (:issue:`318`, :merge:`349`). By `Kyle Brindley`_.

New Features
============
- Add builder-global post action feature to Abaqus journal and Python script builders (:issue:`318`, :merge:`349`). By
  `Kyle Brindley`_.
- Add a ``.gitignore`` file to the ``waves quickstart`` template files (:issue:`324`, :merge:`352`). By `Kyle
  Brindley`_.

Internal Changes
================
- Reduce duplicate code by moving common, required, generate method calls to the ABC abstract method (:issue:`322`,
  :merge:`350`). By `Kyle Brindley`_.
- Update the tutorials directory name. It no longer contains the WAVES-EABM template, which moved to the quickstart
  directory (:issue:`323`, :merge:`351`). By `Kyle Brindley`_.

Enhancements
============
- Accept a list of strings for the ``abaqus_solver`` ``post_action`` argument (:issue:`318`, :merge:`349`). By `Kyle
  Brindley`_.

******************
0.4.7 (2022-09-29)
******************

New Features
============
- Add demonstration PDF report that reuses the documentation source files to the ``waves quickstart`` template files
  (:issue:`305`, :merge:`338`). By `Kyle Brindley`_.
- Add Abaqus solve cpu option as a build action signature escaped sequence in the ``waves quickstart`` template files
  (:issue:`194`, :merge:`341`). By `Kyle Brindley`_.

Bug fixes
=========
- Remove the ``amplitudes.inp`` file which conflicts with the direct displacement specification change introduced in
  :merge:`272` (:issue:`320`, :merge:`346`). By `Kyle Brindley`_.
- Fix the partially broken rectangle simulation schematic in the quickstart template files (:issue:`321`,
  :merge:`347`). By `Kyle Brindley`_.

Documentation
=============
- Add direct links to the Abaqus journal file API/CLI in the tutorials (:issue:`175`, :merge:`337`). By `Kyle
  Brindley`_.
- Add a rough draft "build action signature escape sequence" tutorial to demonstrate escape sequence usage
  (:issue:`194`, :merge:`341`). By `Kyle Brindley`_.
- Update the ``tree`` command usage for consistency across tutorials (:issue:`317`, :merge:`342`). By `Kyle Brindley`_.
- Clarify the usage of `Python pathlib`_ methods to generate the ``solve_source_list`` in :ref:`tutorial_simulation`
  (:issue:`314`, :merge:`343`). By `Thomas Roberts`_.
- Add a theory section to the quickstart template analysis report(s) and fix the images to match the intended simulation
  design (:issue:`320`, :merge:`345`). By `Kyle Brindley`_.

Internal Changes
================
- Remove waves internal import from quickstart files (:issue:`313`, :merge:`339`). By `Kyle Brindley`_.
- Remove the waves internal import from the tutorial files (:issue:`315`, :merge:`340`). By `Kyle Brindley`_.
- Change from a plane strain to plane stress tutorial and quickstart simulation (:issue:`319`, :merge:`344`). By `Kyle
  Brindley`_.
- Change to the Abaqus linear solver in the example simulation (:issue:`320`, :merge:`345`). By `Kyle Brindley`_.

Enhancements
============
- Reduce instances of hardcoded project name in the ``waves quickstart`` template files (:issue:`312`, :merge:`336`). By
  `Kyle Brindley`_.

******************
0.4.6 (2022-09-21)
******************

Internal Changes
================
- Stop webhosting the WAVES-EABM quickstart HTML documentation until the build can be fixed in :issue:`311`
  (:merge:`329`). By `Kyle Brindley`_.
- Test if the Git-LFS configuration errors were the cause of the bad version number and the Gitlab-Pages failures
  (:merge:`330`). By `Kyle Brindley`_.
- Chase the Git-LFS bug with a ``before_script`` debugging statement and ``git lfs install`` (:merge:`331`). By `Kyle
  Brindley`_.
- Test version number and Gitlab-Pages possible fix with a production release (:issue:`306`, :merge:`332`). By `Kyle
  Brindley`_.

******************
0.4.5 (2022-09-21)
******************

Documentation
=============
- Clarify ``waves quickstart`` project directory behavior in the CLI (:merge:`321`). By `Kyle Brindley`_.

Internal Changes
================
- Fix the WAVES-EABM Gitlab-CI pages job. The quickstart WAVES-EABM removed the logic to help find WAVES in the
  repository instead of the Conda environment, so the build commands must modify PYTHONPATH (:issue:`307`,
  :merge:`317`, :merge:`318`). By `Kyle Brindley`_.
- Add Conda managed Git package to the development environment (:issue:`285`, :merge:`322`). By `Kyle Brindley`_.
- Remove unused packages from quickstart template environemnt file (:issue:`309`, :merge:`325`). By `Kyle Brindley`_.
- Remove the duplicate tutorial suite regression tests. WAVES-EABM documentation test build now lives in the quickstart
  template and individual tutorial configuration are tested directly (:issue:`310`, :merge:`326`). By `Kyle Brindley`_.

Enhancements
============
- WAVES ``quickstart`` subcommand no longer preserves source tree read/write meta data (:issue:`304`, :merge:`320`). By
  `Kyle Brindley`_.

******************
0.4.4 (2022-09-19)
******************

New Features
============
- Add a ``waves quickstart`` subcommand to copy the rectangle compression project as a template for a new project.
  Currently limited to the "SCons-WAVES quickstart" tutorial files. (:issue:`284`, :merge:`300`). By `Kyle Brindley`_.
- Add a documentation template to the ``waves quickstart`` subcommand (:issue:`291`, :merge:`314`). By `Kyle Brindley`_.

Documentation
=============
- Update tutorial output examples to match the separation of datacheck and simulation tasks performed in :issue:`244`,
  :merge:`250`. Some of the tutorial body text was missed in the update (:issue:`298`, :merge:`307`). By `Kyle
  Brindley`_.
- Update the Cubit journal file descriptions (:issue:`299`, :merge:`308`). By `Kyle Brindley`_.
- Clarify input and output file extension behavior in the journal file API and CLI (:issue:`301`, :merge:`311`). By
  `Kyle Brindley`_.
- Add analysis report examples to the WAVES-EABM documentation (:issue:`202`, :merge:`313`). By `Kyle Brindley`_.

Internal Changes
================
- Do not install as the deprecated zipped EGG file (:issue:`290`, :merge:`301`). By `Kyle Brindley`_.
- Test the as-installed HTML documentation index file location used by the ``waves docs`` subcommand (:issue:`290`,
  :merge:`301`). By `Kyle Brindley`_.
- Dereference symbolic links during ``copy_substitute`` tasks by default (:issue:`297`, :merge:`303`). By `Kyle
  Brindley`_.
- Ignore ``*.pyc`` and cache files during ``waves quickstart`` project template creation (:issue:`300`, :merge:`310`).
  By `Kyle Brindley`_.
- Ignore the datacheck alias tasks when Abaqus is missing (:issue:`296`, :merge:`312`). By `Kyle Brindley`_.

Enhancements
============
- Implement separate project and simulation configuration files for the ``waves quickstart`` subcommand (:issue:`292`,
  :merge:`302`). By `Kyle Brindley`_.
- Add extraction, post-processing, and global data_check alias to ``waves quickstart`` subcommand (:issue:`293`,
  :merge:`304`). By `Kyle Brindley`_.
- Add a mesh convergence template to the ``waves quickstart`` subcommand (:issue:`294`, :merge:`305`). By `Kyle
  Brindley`_.

******************
0.4.3 (2022-09-13)
******************

Bug fixes
=========
- Match the CSV file name to the H5 target name in the Abaqus extract builder. Will allow multiple tasks to
  extract separate output from the same ODB file (:issue:`287`, :merge:`296`). By `Kyle Brindley`_.
- Match the job name to the output file name instead of the input file name in ``odb_extract`` (:issue:`287`,
  :merge:`296`). By `Kyle Brindley`_.

******************
0.4.2 (2022-09-08)
******************

Breaking changes
================
- Add '_Assembly' to name of assembly instance in hdf5 output of odb_extract. Added to differentiate it from part
  instance of the same name (:issue:`260`, :merge:`263`). By `Prabhu Khalsa`_.

Internal Changes
================
- Use ``scipy`` for latin hypercube sampling instead of ``pyDOE2``. Reduces package dependency count and standardizes
  the current parameter generators on a single package (:issue:`286`, :merge:`293`). By `Kyle Brindley`_.

******************
0.4.1 (2022-09-07)
******************

Breaking changes
================
- Use the same parameter distribution schema as Latin Hypercube in the Sobol Sequence generator (:issue:`282`,
  :merge:`288`). By `Kyle Brindley`_.
- Change the keyword arguments variable name to the more general ``kwargs`` in Latin Hypercube and Sobol Sequence for
  consistency between classes (:issue:`282`, :merge:`288`). By `Kyle Brindley`_.
- Remove the Linux wrapper shell script in favor of merging the ``git clone`` feature with the OS-agnostic ``waves build``
  subcommand (:issue:`283`, :merge:`291`). By `Kyle Brindley`_.

New Features
============
- Experimental waves build command for automatically re-running workflows which extend a parameter study (:issue:`279`,
  :merge:`285`). By `Kyle Brindley`_.
- Add a custom study subcommand to the parameter study CLI (:issue:`276`, :merge:`289`). By `Kyle Brindley`_.
- Add a sobol sequence subcommand to the parameter study CLI (:issue:`277`, :merge:`290`). By `Kyle Brindley`_.
- Add a ``git clone`` feature to the ``waves build`` subcommand (:issue:`282`, :merge:`291`). By `Kyle Brindley`_.

Bug fixes
=========
- Accept any 2D array like for the Custom Study parameter generator (:issue:`276`, :merge:`289`). By `Kyle Brindley`_.

Documentation
=============
- Clarify the WAVES builder behavior of setting the working directory to the parent directory of the first specified
  target (:issue:`265`, :merge:`279`). By `Thomas Roberts`_.
- Complete WAVES Tutorial: Mesh Convergence (:issue:`272`, :merge:`282`). By `Thomas Roberts`_.
- Add Tutorial: Mesh Convergence to the tutorial introduction page (:issue:`281`, :merge:`287`). By `Thomas Roberts`_.

Enhancements
============
- Provide the data downselection dictionary as a CLI argument rather than hardcoding it in ``plot_scatter.py``
  (:issue:`273`, :merge:`281`). By `Thomas Roberts`_.

Internal Changes
================
- Test the parameter study CLI generator sub-commands (:issue:`276`, :merge:`289`). By `Kyle Brindley`_.

******************
0.3.6 (2022-08-31)
******************

New Features
============
- Add a Sobol sequence parameter generator. Requires ``scipy>=1.7.0`` but this is not yet enforced in the Conda package
  runtime requirements. See :issue:`278` for the timeline on the minimum ``scipy`` requirement update (:issue:`274`,
  :merge:`278`). By `Kyle Brindley`_.

Bug fixes
=========
- Use the parameter set name as the parameter study's set index dimension. Fixes unintentional breaking change in the
  parameter study coordinates from :merge:`266` that required users to swap dimensions when merging parameter studies with
  the associated results (:issue:`270`, :merge:`277`). By `Kyle Brindley`_.
- Merge quantiles attribute correctly when provided with a previous parameter study (:issue:`275`, :merge:`280`). By
  `Kyle Brindley`_.

Documentation
=============
- Make typesetting corrections to the WAVES tutorials (:issue:`263`, :merge:`276`). By `Thomas Roberts`_.

Internal Changes
================
- Use vectorized indexing to replace ``nan`` values in ``_ParameterGenerator._update_parameter_set_names()``
  (:issue:`271`, :merge:`275`). By `Matthew Fister`_.

******************
0.3.5 (2022-08-24)
******************

Documentation
=============
- Fix the type hint for the ``previous_parameter_study`` of the paramter generators' API (:merge:`271`). By `Kyle
  Brindley`_.
- Add the parameter study extension feature to the parameter study tutorials (:issue:`267`, :merge:`273`). By `Kyle
  Brindley`_.

Enhancements
============
- Add keyword argument pass through to Latin Hypercube generation (:issue:`261`, :merge:`272`). By `Kyle Brindley`_.
- Use the parameter study extension feature in the ``previous_parameter_study`` interface of the parameter generators
  (:issue:`267`, :merge:`273`). By `Kyle Brindley`_.

Internal Changes
================
- Use ``pyDOE2`` instead of ``smt`` for Latin Hypercube sampling. Implement more rigorous Latin Hypercube parameter
  study unit tests (:issue:`261`, :merge:`272`). By `Kyle Brindley`_.

******************
0.3.4 (2022-08-23)
******************

Breaking changes
================
- Remove the intermediate attributes used to form the parameter study Xarray Dataset from the external API
  (:issue:`268`, :merge:`268`). By `Kyle Brindley`_.

Bug fixes
=========
- Fix parameter set dimensions in tutorial set iteration usage for parameter studies with more than 10 sets
  (:issue:`258`, :merge:`260`). By `Kyle Brindley`_.
- Fix odb_extract to properly parse and store the first data value in the field outputs
  (:issue:`259`, :merge:`261`). By `Prabhu Khalsa`_.

New Features
============
- Add set name template option to the parameter generators and parameter study interfaces. Allow the set name template
  to be changed when writing parameter sets to STDOUT or a single file. (:issue:`253`, :merge:`264`). By `Kyle Brindley`_.
- Add the ability to merge or expand parameter studies without re-building all previously executed SCons parameter sets.
  Feature functions for all parameter generators and the CLI (:issue:`224`, :merge:`266`). By `Kyle Brindley`_.

Documentation
=============
- Separate the parameter study output file template from the set name directories in the WAVES-EABM tutorials
  (:issue:`264`, :merge:`265`). By `Kyle Brindley`_.

Internal Changes
================
- Raise an exception for unsupported output file type strings (:issue:`253`, :merge:`264`). By `Kyle Brindley`_.
- Store the parameter set names as a dictionary mapping the unique parameter set hash to the set name (:issue:`268`,
  :merge:`268`). By `Kyle Brindley`_.

******************
0.3.3 (2022-08-09)
******************

Bug fixes
=========
- Look outside the ``noarch`` installation egg to find the installed documentation files (:issue:`249`, :merge:`248`).
  By `Kyle Brindley`_.
- odb_extract can now handle multiple 'Component of field' headers if they are present within field data sections
  (:issue:`254`, :merge:`255`). By `Prabhu Khalsa`_.
- Fix unintentional type casting in the parameter study conversion to dict (:issue:`255`, :merge:`257`). By `Kyle
  Brindley`_.

New Features
============
- Add CustomStudy parameter study generator (:issue:`231`, :merge:`224`). By `Matthew Fister`_.

Documentation
=============
- Add bibliography citations to match external URLs hyperreferences (:issue:`242`, :merge:`249`). By `Kyle Brindley`_.
- Add a draft outline of a regression test tutorial (:issue:`162`, :merge:`251`). By `Kyle Brindley`_.
- Add references and citations to tutorials (:issue:`252`, :merge:`253`). By `Kyle Brindley`_.
- Add discussion to the data extraction tutorial (:issue:`104`, :merge:`254`). By `Kyle Brindley`_.

Internal Changes
================
- Separate the WAVES-EABM datacheck tasks from the main simulation workflow (:issue:`244`, :merge:`250`). By `Kyle
  Brindley`_.

Enhancements
============
- Redirect the ``rm`` command STDOUT and STDERR from the abaqus extract builder to a unique filename (:issue:`250`,
  :merge:`252`). By `Kyle Brindley`_.

******************
0.3.2 (2022-08-04)
******************

Bug fixes
=========
- Remove redundant parameter file dependency from WAVES-EABM parameter substitution tutorial source files (:issue:`246`,
  :merge:`243`). By `Kyle Brindley`_.

New Features
============
- Create a ``waves`` command-line utility with a version argument and a subparser for opening the packaged HTML
  documentation in the system default web browser (:issue:`172`, :merge:`233`). By `Thomas Roberts`_.
- Add a Conda environment builder to aid in Python software stack documentation for reproducibility (:issue:`212`,
  :merge:`239`). By `Kyle Brindley`_.
- Add a substitution syntax helper to prepend and append special characters on dictionary key strings (:issue:`235`,
  :merge:`240`). By `Kyle Brindley`_.

Documentation
=============
- Standardize on 'project configuration' language to describe SCons scripts: SConstruct and SConscript (:issue:`134`,
  :merge:`237`). By `Kyle Brindley`_.
- Update the tutorial discussions about the simulation variables dictionary usage (:issue:`243`, :merge:`241`). By `Kyle
  Brindley`_.
- Standardize the WAVES-EABM parameter set module names (:issue:`245`, :merge:`242`). By `Kyle Brindley`_.
- Discuss task signatures related to parameter set values in the WAVES-EABM parameter substitution tutorial
  (:issue:`246`, :merge:`243`). By `Kyle Brindley`_.

Internal Changes
================
- Update the WAVES-EABM journal and python files for the PEP-8 style guide (:issue:`190`, :merge:`236`). By `Kyle
  Brindley`_.
- Remove the Abaqus keyword ``*PARAMETER`` from the parameter substitution tutorial because it's not supported for input
  file import to CAE. (:issue:`240`, :merge:`238`). By `Kyle Brindley`_.
- In WAVES-EABM, use parameter name keys without substitution syntax and perform substitution syntax key string changes
  only when necessary for parameter substitution (:issue:`243`, :merge:`241`). By `Kyle Brindley`_.
- Standardize the WAVES-EABM parameter set module names (:issue:`245`, :merge:`242`). By `Kyle Brindley`_.
- Standardize code snippet markers in tutorial configuration files to reduce diff clutter in the documentation
  (:issue:`247`, :merge:`245`). By `Kyle Brindley`_.

******************
0.3.1 (2022-08-02)
******************

Breaking changes
================
- Change the parameter study data key from 'values' to 'samples' to avoid name clash with the 'values' method and
  attribute of dictionaries and datasets. (:issue:`234`, :merge:`229`). By `Kyle Brindley`_.
- Re-organize the parameter study coordinates to allow mixed types, e.g. one parameter that uses strings and another
  that uses floats (:issue:`239`, :merge:`234`). By `Kyle Brindley`_.

Bug fixes
=========
- Add construction environment variables to the Abaqus extract builder signature. Builder now re-executes when the
  keyword arguments change (:issue:`230`, :merge:`232`). By `Kyle Brindley`_.
- Re-organize the parameter study coordinates to allow mixed types, e.g. one parameter that uses strings and another
  that uses floats. Fixes the parameter study read/write to h5 files to avoid unexpected type conversions (:issue:`239`,
  :merge:`234`). By `Kyle Brindley`_.

Documentation
=============
- Complete WAVES Tutorial 07: Cartesian Product (:issue:`103`, :merge:`152`). By `Thomas Roberts`_.

Internal Changes
================
- Simpler parameter study unpacking into the parameter set task generation loop (:issue:`238`, :merge:`230`). By `Kyle
  Brindley`_.

******************
0.2.2 (2022-07-28)
******************

Breaking changes
================
- Parmeter study writes to YAML syntax by default to provide syntactically correct STDOUT default behavior. Note that
  the ``write()`` feature isn't used in the WAVES-EABM tutorials, so the user manual documentation is unchanged.
  (:issue:`218`, :merge:`212`). By `Kyle Brindley`_.
- Remove the parameter study python syntax output. Recommend using YAML syntax and the PyYAML package if parameter study
  output files must use a text based serialization format. (:issue:`223`, :merge:`217`). By `Kyle Brindley`_.

New Features
============
- Add the latin hypercube generator to the parameter study command-line utility (:issue:`216`, :merge:`207`). By `Kyle
  Brindley`_.
- Accept output template pathlike strings and write parameter study meta file in the same parent directory as the
  parameter set files (:issue:`79`, :merge:`210`). By `Kyle Brindley`_.
- Add the option to output the parameter study sets as Xarray Dataset H5 files (:issue:`218`, :merge:`212`). By `Kyle
  Brindley`_.
- Add the option to output the parameter study as a single file (:issue:`222`, :merge:`218`). By `Kyle Brindley`_.

Bug fixes
=========
- Fix the representation of strings in the parameter generator parameter set output files (:issue:`215`, :merge:`206`).
  By `Kyle Brindley`_.
- Fix the parameter study meta file write behavior to match documentation (:merge:`209`). By `Kyle Brindley`_.

Documentation
=============
- Provide Abaqus files in the appendix for users without access to the WAVES or WAVES-EABM repository files
  (:issue:`206`, :merge:`203`). By `Kyle Brindley`_.
- Remove the ABC ParameterGenerator abstract method docstrings from the parameter generators' APIs (:issue:`213`,
  :merge:`204`). By `Kyle Brindley`_.
- Clarify parameter generator behavior in external APIs. Add ABC write method docstring to parameter generators' APIs.
  (:issue:`195`, :merge:`214`). By `Kyle Brindley`_.
- Placeholder structure for work-in-progress post-processing tutorial (:issue:`95`, :merge:`215`). By `Kyle Brindley`_.

Internal Changes
================
- Add cartesian product schema validation (:issue:`80`, :merge:`208`). By `Kyle Brindley`_.
- Avoid file I/O during parameter study write pytests (:issue:`217`, :merge:`211`). By `Kyle Brindley`_.
- Add matplotlib to the CI environment for the pending post-processing tutorial (:issue:`221`, :merge:`216`). By `Kyle
  Brindley`_.
- Add configuration and integration test files for a post-processing demonstration, including merging a parameter study
  with the results data. (:issue:`95`, :merge:`215`). By `Kyle Brindley`_.
- Simplify the WAVES-EABM parameter study variables and their usage in the simulation configuration files (:issue:`219`,
  :merge:`221`). By `Kyle Brindley`_.
- Changed validated to verified in WAVES acronym as it better reflects the intent of the tool (:issue:`220`,
  :merge:`222`). By `Kyle Brindley`_.

Enhancements
============
- Construct WAVES and WAVES-EABM alias list from SCons configuration (:issue:`56`, :merge:`213`). By `Kyle Brindley`_.
- Add the ``scipy.stats`` parameter name to distribution object mapping dictionary as the ``parameter_distributions``
  attribute of the ``LatinHypercube`` class for use by downstream tools and workflows (:issue:`228`, :merge:`220`). By
  `Kyle Brindley`_.
- Avoid type conversions with mixed type cartesian product parameter studies (:issue:`225`, :merge:`223`). By `Kyle
  Brindley`_.

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

Documentation
=============
- Update Scons terminal output and sample tree output in the tutorials to reflect the state of a user's tutorial files
  (:issue:`189`, :merge:`174`). By `Thomas Roberts`_.
- Add a pure SCons quickstart tutorial (:issue:`48`, :merge:`173`). By `Kyle Brindley`_.

Internal Changes
================
- Reduce the simulation variables and substitution dictionary to a single dictionary (:issue:`181`, :merge:`177`). By
  `Kyle Brindley`_.

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
- Convert project command-line variables to command-line options (:issue:`179`, :merge:`169`). By `Kyle Brindley`_.

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
- Move the build wrapper discussion and usage into the command-line utilities section (:issue:`168`, :merge:`143`). By
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
- Add a quickstart tutorial using a single project configuration file (:issue:`147`, :merge:`113`). By `Kyle Brindley`_.
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
- Add the command-line tools odb_extract, msg_parse, and sta_parse (:issue:`93`, :merge:`88`). By `Prabhu Khalsa`_.

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
- Create per-tutorial EABM stub project configuration files (SConstruct) to aid in incremental changes in the tutorial
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
- Make the variant (build) directory a command-line variable option (:issue:`25`, :merge:`29`). By `Kyle Brindley`_.
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
- Add a command-line interface (CLI) documentation page (:issue:`44`, :merge:`34`). By `Thomas Roberts`_.
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
- Separate the common custom builders from the EABM SCons project configuration (:issue:`19`, :merge:`11`). By `Kyle
  Brindley`_.
- Add a variable to pass through additional Abaqus command-line arguments to the Abaqus journal file builder
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
