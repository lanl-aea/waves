#! /usr/bin/env python
#
# Inherit the parent construction environment
Import('source_dir')

Command(target=f"{source_dir}/README.txt",
        source="README.rst",
        action=Copy("$TARGET", "$SOURCE"))

Command(target=f"{source_dir}/quickstart_README.txt",
        source="quickstart/README.rst",
        action=Copy("$TARGET", "$SOURCE"))

Command(target=f"{source_dir}/environment.txt",
        source="environment.txt",
        action=Copy("$TARGET", "$SOURCE"))
