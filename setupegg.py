#!/usr/bin/env python
"""Wrapper to run setup.py using setuptools."""

# Import setuptools and call the actual setup
import setuptools
exec(compile(open('setup.py').read(), 'setup.py', 'exec'))
