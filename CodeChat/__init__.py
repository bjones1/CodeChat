# .. -*- coding: utf-8 -*-
#
#    Copyright (C) 2012-2014 Bryan A. Jones.
#
#    This file is part of CodeChat.
#
#    CodeChat is free software: you can redistribute it and/or modify it under
#    the terms of the GNU General Public License as published by the Free
#    Software Foundation, either version 3 of the License, or (at your option)
#    any later version.
#
#    CodeChat is distributed in the hope that it will be useful, but WITHOUT ANY
#    WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#    FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
#    details.
#
#    You should have received a copy of the GNU General Public License along
#    with CodeChat.  If not, see <http://www.gnu.org/licenses/>.
#
# *********************************
# __init__.py - Package placeholder
# *********************************
# This file defines this directory as a Python package, which contains the
# CodeChat application.
#
# Give the version number, which is read by :doc:`../setup.py` during packaging.
# This is chosen following the `version convention
# <http://packaging.python.org/en/latest/tutorial.html#version>`_.
__version__ = '0.0.18'

# Import all the non-test modules in this package.
from . import CodeToRest, CodeToRestSphinx, LanguageSpecificOptions
