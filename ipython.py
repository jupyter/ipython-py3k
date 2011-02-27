#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""IPython -- An enhanced Interactive Python

The actual ipython script to be installed with 'python setup.py install' is
in './IPython/scripts' directory. This file is here (ipython source root
directory) to facilitate non-root 'zero-installation' (just copy the source tree
somewhere and run ipython.py) and development. """

# Ensure that the imported IPython is the local one, not a system-wide one
import os, sys
this_dir = os.path.dirname(sys.argv[0])
sys.path.insert(0, this_dir)

# Now proceed with execution
exec(compile(open(os.path.join(
    this_dir, 'IPython', 'scripts', 'ipython3'
)).read(), os.path.join(
    this_dir, 'IPython', 'scripts', 'ipython3'
), 'exec'))
