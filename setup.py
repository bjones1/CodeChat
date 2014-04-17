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
# ***************************************
# setup.py - Package and install CodeChat
# ***************************************
# Builds and installs CodeChat.
#
# Packaging notes
# ===============
# Packaging on Python is a mess, IMHO. A quick summary: distutils can't
# install dependencies from PyPi, so use setuptools. A source distribution is a
# good idea becaues it can run on a bare Python installation with no other
# installs required, but there's no standard format (.zip?, .tar.gz?, etc.). An .egg is
# nice, but requires setuptools/pip/ez_setup installed. The .whl (Python wheel)
# is the latest and greatest format that superceeds eggs, but with similar
# problems (requires wheel to be installed).
#
# Reading to get up to speed:
#
# * `Python Packaging User Guide`_ - the most up-to-date reference I've found
#   so far. Tells which tools to actually use.
#
#   .. _`Python Packaging User Guide`: http://packaging.python.org/en/latest/
#
# * `The Hitchhiker's Guide to Packaging`_: Outdated, unfortunatly, but used to
#   be helpful.
#
#   .. _`The Hitchhiker's Guide to Packaging`: http://guide.python-distribute.org/
#
# * `How To Package Your Python Code`_: A useful tutorial on what to do. Doesn't
#   cover eggs/wheels, though.
#
#   .. _`How To Package Your Python Code`: http://www.scotttorborg.com/python-packaging/index.html
#
# * distutils_ - The built-in installer. Tells what to do, but not what actually
#   happens. It doesn't have the ability to install dependencies
#   from PyPi_, which I need.
#
#   .. _distutils: http://docs.python.org/distutils/index.html
#   .. _PyPi: http://pypi.python.org>
#
# * setuptools_ - A distutils replacement which can install dependencies, so I
#   use it.
#
#   .. _setuptools: https://pythonhosted.org/setuptools
#
# Questions / to do
# =================
# * Do I need to specify ez_setup.py in my MANIFEST.in?
#
# To package
# ==========
# * Create a source distribution:
#
#   ``python setup.py sdist``
#
# * Create a binary distribution:
#
#   ``python setup.py bdist_wheel``
#
# Packaging script
# ================
# Otherwise known as the evils of setup.py.
#
# To package data files, I'm using ``include_package_data = True`` then putting
# the files in MANIFEST.in (see
# http://pythonhosted.org/setuptools/setuptools.html#including-data-files).
#
# For users who install this that don't have setuptools installed already (see
# https://pythonhosted.org/setuptools/setuptools.html#using-setuptools-without-bundling-it):
import ez_setup
ez_setup.use_setuptools()

from setuptools import setup

# PyPA copied code
# ----------------
# From https://github.com/pypa/sampleproject/blob/master/setup.py, find a
# built-in version number.
import codecs
import os
import re

here = os.path.abspath(os.path.dirname(__file__))

# Read the version number from a source file.
# Why read it, and not import?
# see https://groups.google.com/d/topic/pypa-dev/0PkjVpcxTzQ/discussion
def find_version(*file_paths):
    # Open in Latin-1 so that we avoid encoding errors.
    # Use codecs.open for Python 2 compatibility
    with codecs.open(os.path.join(here, *file_paths), 'r', 'latin1') as f:
        version_file = f.read()

    # The version line must have the form
    # __version__ = 'ver'
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")

# Get the long description from the relevant file
with codecs.open('README.rst', encoding='utf-8') as f:
    long_description = f.read()

# My code
# -------
setup(name='CodeChat',
      version=find_version('CodeChat', '__init__.py'),
      description="The CodeChat system for software documentation",
      long_description=long_description,
      author="Bryan A. Jones",
      author_email="bjones AT ece.msstate.edu",
      url='https://bitbucket.org/bjones/documentation/overview',
      classifiers=['Development Status :: 3 - Alpha',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
                   'Operating System :: OS Independent',
                   'Natural Language :: English',
                   'Programming Language :: Python',
                   'Topic :: Software Development :: Documentation',
                   'Topic :: Text Processing :: Markup',
                  ],
      install_requires=['docutils >= 0.11', ],
      packages = ['CodeChat'],
      include_package_data = True,
      )
