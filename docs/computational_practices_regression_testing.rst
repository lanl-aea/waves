.. _testing:

******************
Regression Testing
******************

There are several types of testing performed in software development. The three most relevant to :term:`modsim
repositories` are unit, integration, and system testing. Executing the test suite at regular intervals or after making
changes to a project is called regression testing. If the regression test suite is performed prior to merging any change
to a project, it is called continuous testing.

Since :term:`modsim repositories` will inevitably involve some amount of scripting and may contain small,
project-specific reusable libraries, it is important to learn the practices of software testing. However, these testing
concepts can also be applied to a simulation workflow to verify that changes to the simulation files and
simulation-construction tools have not broken the workflow.

Unit testing is directed at the interface and behavior of an individual function, method, or class. Unit testing in a
modsim repository serves the same purposes as in software development, and should be implemented to verify the behavior
of supporting scripts and project libraries. The intent is to test the code specific to the project, so unit tests
should avoid testing the behavior of libraries external to the current modsim project. Because well-defined behavior is
difficult to implement and difficult to verify when a section of code performs many distinct operations, best practice
is to write small, single-purpose functions and  methods. This makes them easier to document, implement, test, and
maintain. In :term:`modsim repositories`, it is rare to write project-specific file input and output (I/O) operations, so
the project unit tests should usually avoid real I/O operations that read or create files on disk. Instead, most
programming languages have unit-testing frameworks that include mock objects. Mock objects can be used in place of
external library calls to avoid file I/O, while still allowing aspects of the library call to be examined in unit
testing, e.g., what arguments and values were passed to the mock object. Finally, unit testing verifies the interfaces of
code, leaving developers free to change the implementation without creating breaking changes in code behavior.

Integration testing is the practice of testing interfaces between functions, methods, or classes. Where unit testing
verifies the documented interface and behavior of a single unit of code, integration testing verifies that the
various elements of a script or library work together as intended. Similar to unit testing, integration testing is
limited to the current project's code. If the scope of integration testing covers code elements exposed to the end user,
e.g., the simulation scripts constructing a workflow, it can be considered a verification of the intended usage. Where
unit testing verifies a single code element's interface, integration testing verifies the intended usage of the script
or library.

When testing includes file I/O or external executables and programs, it is often called system testing. In a modsim
repository, integration testing may require execution of several standalone scripts, such as those introduced in
:ref:`tutorial_geometry` and :ref:`tutorial_partition_mesh`, which communicate through file I/O operations and must be
executed by external software. For this reason, this project will often use integration and system testing
interchangeably. Unless a :term:`modsim repository` contains project specific, reusable libraries, most integration
testing of a simulation workflow will actually be system testing. One important aspect of such system testing is to
provide a regression test suite that will verify expected behavior when external libraries, programs, and software
change versions or when executing the simulation on a new server. Regular execution of the modsim integration and system
tests helps catch breaking changes in external dependencies shortly after changes in the system software and
architecture have been made.

Finally, regression testing may take several forms depending on the cost of test-suite execution. In modsim
repositories, it is good to perform unit and integration testing on any project-specific code prior to every proposed
change. Relative to simulation workflow integration tests, testing a code base is relatively quick and inexpensive and
can usually be performed at daily or even hourly intervals as small, single-purpose changes are made incrementally.
Such continuous testing of regression tests can be performed by manual kickoff of the regression test suite but is
often implemented in an automated continuous integration (CI) framework.

Full-simulation workflow testing is often computationally expensive and time consuming. Instead of testing with every
proposed change to the project, it may be more appropriate to schedule a separate collection of tests for regular
execution. Depending on the resources required, this may be as frequent as nightly (during server low use periods) or as
infrequently as annually. It is desirable to catch potential problems as early as possible, so it is worth the time to
subdivide scheduled tests across several scheduled intervals, where the longer-interval tests perform an increasing
portion of the full test suite. It is also helpful to run the inexpensive part of a simulation workflow as frequently as
possible. For instance, a project might test the workflow preceding the numeric solver weekly but test the workflow
from the solver onward monthly, quarterly, or annually. Annual testing should be avoided, but at the very least, testing
before and after a system change or software upgrade will help identify if the problem is related to that change.
