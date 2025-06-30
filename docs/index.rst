.. only:: epub

   .. include:: epub_copyright.txt

#########
|project|
#########

.. include:: project_brief.txt

.. raw:: latex

   \part{Computational Practices}

.. _computational_tools:

.. toctree::
   :hidden:
   :maxdepth: 1
   :caption: Computational Practices

   computational_practices_introduction
   computational_practices_version_control
   computational_practices_documentation
   computational_practices_build_system
   computational_practices_compute_environment
   computational_practices_regression_testing
   computational_practices_archival

.. raw:: latex

   \part{User Manual}

.. _user_manual:

.. toctree::
   :hidden:
   :maxdepth: 1
   :caption: User Manual

   abstract
   installation
   tutorial_quickstart
   tutorial_introduction
   tutorial_core
   tutorial_supplemental
   tutorial_wip
   templates
   api
   cli

.. raw:: latex

   \part{Help and Reference}

.. toctree::
   :hidden:
   :caption: Help and Reference
   :maxdepth: 1

   license
   citation
   internal_api
   devops
   release_philosophy
   changelog
   zreferences
   glossary

.. raw:: latex

   \part{Appendices}

.. toctree::
   :hidden:
   :caption: Appendices
   :maxdepth: 1

   tutorial_api
   tutorial_cli

.. raw:: latex

   \part{Indices and Tables}

.. only:: html and aea

   .. |aea-release| image:: https://re-git.lanl.gov/aea/python-projects/waves/-/badges/release.svg?key_text=re-git%20release
      :target: https://re-git.lanl.gov/aea/python-projects/waves/-/releases

   .. |aea-main| image:: https://re-git.lanl.gov/aea/python-projects/waves/badges/main/pipeline.svg?key_text=re-git%20latest&key_width=80
      :target: https://re-git.lanl.gov/aea/python-projects/waves/-/pipelines

   .. |aea-coverage| image:: https://re-git.lanl.gov/aea/python-projects/waves/badges/main/coverage.svg?job=aea-developer-test&key_text=re-git%20latest&key_width=80
      :target: https://re-git.lanl.gov/aea/python-projects/waves/-/pipelines

   |aea-release| |aea-main| |aea-coverage|

.. only:: html

   .. include:: README.txt
      :start-after: badges-start-do-not-remove
      :end-before: badges-end-do-not-remove

   |

   .. grid:: 1 2 2 2
      :gutter: 2
      :margin: 2

      .. grid-item-card:: :octicon:`book` Computational Practices
         :link: practices_introduction
         :link-type: ref

         Computional science and engineering practices primer with a recommended practical curriculum

      .. grid-item-card:: :octicon:`light-bulb` Why |PROJECT|?
         :link: abstract
         :link-type: ref

         Four paragraph motivation for build systems and |PROJECT| in computational science and engineering

      .. grid-item-card:: :octicon:`download` Installation
         :link: installation
         :link-type: ref

         Installation with conda-forge or PyPI

      .. grid-item-card:: :octicon:`rocket` Quickstart
         :link: tutorial_quickstart
         :link-type: ref

         Minimal working examples of build system integration with parameter studies

      .. grid-item-card:: :octicon:`mortar-board` Tutorials
         :link: tutorial_introduction
         :link-type: ref

         Introduction to the full tutorial suite

      .. grid-item-card:: :octicon:`repo-template` Modsim Templates
         :link: modsim_templates
         :link-type: ref

         Start from a modsim template project

      .. grid-item-card:: :octicon:`code-square` API
         :link: external_api
         :link-type: ref

         Public application program interface (API)

      .. grid-item-card:: :octicon:`command-palette` CLI
         :link: cli
         :link-type: ref

         Public command line interface (CLI)
