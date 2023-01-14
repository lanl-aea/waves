.. _changelog:

#########
Changelog
#########

******************
0.6.3 (unreleased)
******************

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
- Change post processing script name in the tutorials and quickstart template files to match broader scope
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
- Add demonstration PDF report that re-uses the documentation source files to the ``waves quickstart`` template files
  (:issue:`305`, :merge:`338`). By `Kyle Brindley`_.
- Add Abaqus solve cpu option as a build action signature escaped sequence in the ``waves quickstart`` template files
  (:issue:`194`, :merge:`341`). By `Kyle Brindley`_.

Bug fixes
=========
- Remove the ``amplitudes.inp`` file which conflicts with the direct displacement specification change introduced in
  :merge:`272` (:issue:`320`, :merge:`346`). By `Kyle Brindley`_.
- Fix the partially broken single element simulation schematic in the quickstart template files (:issue:`321`,
  :merge:`347`). By `Kyle Brindley`_.

Documentation
=============
- Add direct links to the Abaqus journal file API/CLI in the tutorials (:issue:`175`, :merge:`337`). By `Kyle
  Brindley`_.
- Add a rough draft "build action signature escape sequence" tutorial to demonstrate escape sequence usage
  (:issue:`194`, :merge:`341`). By `Kyle Brindley`_.
- Update the ``tree`` command usage for consistency across tutorials (:issue:`317`, :merge:`342`). By `Kyle Brindley`_.
- Clarify the usage of `Python pathlib`_ methods to generate the ``solve_source_list`` in :ref:`tutorial_simulation_waves`
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
- Add a ``waves quickstart`` subcommand to copy the single element compression project as a template for a new project.
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
- Create a ``waves`` command line utility with a version argument and a subparser for opening the packaged HTML
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
- Add the latin hypercube generator to the parameter study command line utility (:issue:`216`, :merge:`207`). By `Kyle
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
- Separate the common custom builders from the EABM SCons project configuration (:issue:`19`, :merge:`11`). By `Kyle
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
