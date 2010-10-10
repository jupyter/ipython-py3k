# encoding: utf-8
"""
A simple utility to import something by its string name.

Authors:

* Brian Granger
"""

#-----------------------------------------------------------------------------
#  Copyright (C) 2008-2009  The IPython Development Team
#
#  Distributed under the terms of the BSD License.  The full license is in
#  the file COPYING, distributed as part of this software.
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
# Functions and classes
#-----------------------------------------------------------------------------

def import_item(name):
    """Import and return bar given the string foo.bar."""
    package = '.'.join(name.split('.')[0:-1])
    obj = name.split('.')[-1]
    if package:
        module = __import__(package,fromlist=[obj])
        return module.__dict__[obj]
    else:
        return __import__(obj)

