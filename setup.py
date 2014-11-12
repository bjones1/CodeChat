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
# Packaging on Python is a mess, IMHO. It takes an easy job and makes it hard.
#
# A quick summary: distutils_ can't
# install dependencies from PyPi_, so use setuptools_. A source distribution is a
# good idea becaues it can run on a bare Python installation with no other
# installs required, but there's no standard format (.zip?, .tar.gz?, etc.). An .egg is
# nice, but requires setuptools/pip/ez_setup installed. The .whl
# (`Python wheel <http://wheel.readthedocs.org/en/latest/>`_)
# is the latest and greatest format that superceeds eggs, but with similar
# problems (requires wheel to be installed).
#
# Reading to get up to speed:
#
# * `Python Packaging User Guide <http://packaging.python.org/en/latest/>`_ -
#   the most up-to-date reference I've found so far. Tells which tools to
#   actually use. It was `forked <http://packaging.python.org/en/latest/history.html#id2>`__
#   from `The Hitchhiker's Guide to Packaging <http://guide.python-distribute.org/>`_,
#   which is outdated, unfortunately, but used to be helpful.
#
# * `How To Package Your Python Code <http://www.scotttorborg.com/python-packaging/index.html>`_:
#   A useful tutorial on what to do. Doesn't cover eggs/wheels, though.
#
# * `distutils <http://docs.python.org/distutils/index.html>`_ - The built-in
#   installer. Tells what to do, but not what actually happens. It doesn't have
#   the ability to install dependencies from `PyPi <http://pypi.python.org>`_,
#   which I need.
#
# * `setuptools <https://pythonhosted.org/setuptools>`_ - A distutils
#   replacement which can install dependencies, so I use it.
#
# Questions / to do
# =================
# * Build the docs and post them on the web. See
#   http://pythonhosted.org/setuptools/setuptools.html#upload-docs-upload-package-documentation-to-pypi.
# * Is there any reason for me to distribute my files as a wheel? It's helpful
#   that the Python version is clearly specified (it's not in a source
#   distribution and I can't figure out how to do that), but that's about it.
# * Use this to build Linux packages.
#
#   * Hopefully ``setup.py bdist_rpm``. But Tarek (the `author <https://bitbucket.org/tarek/distribute/wiki/Home>`_ of distribute) says `bdist_rpm is dead <http://ziade.org/2011/03/25/bdist_rpm-is-dead-long-life-to-py2rpm/>`__, and suggests his own tool, pypi2rpm, which is `mostly inactive <https://bitbucket.org/tarek/pypi2rpm>`__.
#   * Maybe `stdeb <https://pypi.python.org/pypi/stdeb>`_, but this is also mostly inactive.
#   * There's `up-to-date docs <https://wiki.debian.org/Python/LibraryStyleGuide>`__ on Debian Python builds that doesn't seem too painful.
#   * The `openSUSE packing python page <https://en.opensuse.org/openSUSE:Packaging_Python>`_ is up to date, and suggests using `py2pack <https://pypi.python.org/pypi/py2pack>`_, another recently-updated tool.
#
#   Based on the above discussion, my ideas:
#
#   * Host all my builds on OBS, and create a cross-platform build there.
#   * Use py2pack to generate an openSUSE package, then manually edit as necessary to get it building with Fedora.
#   * Use stdeb to generate the Debian package, then hand-edit per the Debian docs.
# * Add a `setup.cfg <https://docs.python.org/2/distutils/configfile.html>`_ with defaults.
#
# To package
# ==========
# Create a source distribution, a built distribution, then upload both:
#
#   ``python setup.py sdist bdist_wheel upload``
#
# For `development <https://pythonhosted.org/setuptools/setuptools.html#development-mode>`_
#
#  ``python setup.py develop``
#
# Packaging script
# ================
# Otherwise known as the evils of setup.py.
#
# For users who install this from source but don't have setuptools installed,
# `auto-install it <https://pythonhosted.org/setuptools/setuptools.html#using-setuptools-without-bundling-it>`__.
import ez_setup
ez_setup.use_setuptools()

from setuptools import setup

# PyPA copied code
# ----------------
# From https://github.com/pypa/sampleproject/blob/master/setup.py, find a
# built-in version number and read ``long_description`` from a file.
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
    readme_text = f.read()
    # We just want text up to the contents, so exclude the rest. Side note:
    # README.rst uses DOS newlines (\\r\\n), but
    # codecs (unlike Python's plain open)
    # does not translate DOS line endings to Unix. These are preserved;
    # see second note under
    # ``codecs.open`` in the `docs <https://docs.python.org/2/library/codecs.html>`__.
    # Hence, search for the contents tag, not newlines.
    ##print(readme_text)
    long_description = readme_text[:readme_text.index('.. contents::')]
    ##print(long_description)

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
      install_requires=['docutils >= 0.12', ],
      packages = ['CodeChat'],
      # To package data files, I'm using ``include_package_data = True`` then putting
      # the files in MANIFEST.in (see
      # http://pythonhosted.org/setuptools/setuptools.html#including-data-files).
      include_package_data = True,
      )
