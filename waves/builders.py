#! /usr/bin/env python
import warnings
from waves.scons import *

warnings.simplefilter('always', DeprecationWarning)
message = "The 'waves.builders' module will be deprecated in a future version. Use the 'waves.scons' module instead"
warnings.warn(message, DeprecationWarning)
