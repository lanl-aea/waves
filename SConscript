#! /usr/bin/env python
#
# Inherit the parent construction environment
Import('documentation_source_dir')

Command(target=f"{documentation_source_dir}/README.txt",
        source="README.rst",
        action=Copy("$TARGET", "$SOURCE"))

Command(target=f"{documentation_source_dir}/environment.txt",
        source="environment.txt",
        action=Copy("$TARGET", "$SOURCE"))
