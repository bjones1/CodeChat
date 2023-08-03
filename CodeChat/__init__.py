# .. Copyright (C) 2012-2022 Bryan A. Jones.
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
# ****************************
# |docname| - CodeChat Package
# ****************************
# This file defines this directory as a Python package, which contains the
# CodeChat application.
#
# .. digraph:: Overview
#
#   "Source code" -> "ReST" [label="code_to_rest"]
#   "ReST" -> "HTML" [label="docutils.publish_string\lSphinx\l"]
#   "HTML" -> "ReST" [label="html_to_rest"]
#
#
# Give the version number, which is read by `../setup.py` during packaging.
# This is chosen following the `version convention
# <http://packaging.python.org/en/latest/tutorial.html#version>`_.
__version__ = "1.9.3"
