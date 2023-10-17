.. _releasephilosophy:

##################
Release Philosophy
##################

This section discusses topics related to |project| releases and version numbering.

***************
Version Numbers
***************

The |project| project follows the `PEP-440`_ standard for version numbering. The
production release version number uses the three component ("major.minor.micro")
scheme. The developer (a.k.a. dev) version number follows the production
release number with an appended ".dev" local version number. The version numbers
correspond to git tags in the `upstream repository`_ which point to a static
release of the |project| project.

Because the deployed release of the developer version is constantly updated
against development work, the version number found in the developer version
contains additional information. During deployment, the developer version number
is appended with the git information from the most recent build. This
information contains the most recent git tag ("major.minor.micro+dev") followed
by the number of commits since the last production release and a short hash.

Major Number
============

The major number is expected to increment infrequently. After the first major release, it is recommended that the major
version number only increments for major breaking changes.

Minor Number
============

The minor number is updated for the following reasons:

* New features
* Major internal implementation changes
* Non-breaking interface updates

Incrementing the minor version requires a manual update to the release number found in the Git tags on a
dedicated release commit. Until the first major release, minor version changes may also contain breaking changes. It is
recommended that all minor version changes are announced to the user community prior to release.

Micro Number
============

The micro number is automatically incremented after any merge from the
development (dev) branch into the production (main) branch. The micro version
number indicates the following changes:

* Bug fixes
* Minor internal implementation changes

Until the first major release, micro version number releases may be made without announcement at the discretion of the
lead developer. It is recommended that the developer community periodically discuss priorities for minor version release
with the user community.

.. _releasebranchreq:

***************************
Release Branch Requirements
***************************

All production releases require a release branch. Releases correspond to a variety of bug fixes and features that
characterize the release, as documented in :ref:`changelog`.

The following steps will trigger a micro bump. Major and minor version bumps require a manual Git tag update for the
otherwise automated ``setuptools_scm`` SCM version.

Steps needed for a release include:

1. Create a release branch.
2. Modify ``docs/changelog.rst`` to move version number for release MR commit,
   add a description as relevant, and update any missing entries in the changelog.
3. Commit changes and submit a merge request to the ``dev`` branch at the `upstream repository`_.
4. **Major and Minor bumps ONLY**: Create a new developer version tag, e.g. ``?.?.0+dev``, on the new commit.
   Reset all numbers to the right of the bump to ``0``, e.g. ``1.2.3`` becomes ``2.0.0+dev`` for a Major version
   bump or ``1.3.0+dev`` for a Minor version bump.

   .. code-block:: bash

       $ git tag 1.7.0+dev

5. Push release branch with the new tag

   .. code-block:: bash

       $ git push origin <release branch name>
       $ git push --tags

6. Submit a merge request to the ``dev`` branch of the `upstream repository`_.
7. Immediately submit a ``dev->main`` MR after merging the release branch to ``dev``.
8. Review tests and notes, receive approval, and merge to ``main``.
