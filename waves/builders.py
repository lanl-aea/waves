#! /usr/bin/env python
import warnings
from waves.scons import *

# TODO: Remove the builders module for v1.0
# https://re-git.lanl.gov/aea/python-projects/waves/-/issues/511
warnings.simplefilter('always', DeprecationWarning)
message = "The 'waves.builders' module will be deprecated in a future version. Use the 'waves.scons' module instead"
warnings.warn(message, DeprecationWarning)
