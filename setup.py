# .. Copyright (C) 2012-2017 Bryan A. Jones.
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
# Reading to get up to speed:
#
# * `Python Packaging User Guide <http://packaging.python.org/en/latest/>`_ -
#   the most up-to-date reference I've found so far. Tells which tools to
#   actually use.
#
# * `setuptools <https://pythonhosted.org/setuptools>`_ - A distutils
#   replacement which can install dependencies, so I use it.
#
# .. _to-package:
#
# To package
# ==========
# Create a source distribution, a built distribution, then upload both to
# `CodeChat at PyPI <https://pypi.python.org/pypi/CodeChat>`_::
#
#   python -m pip install -U pip setuptools wheel twine
#   python setup.py sdist bdist_wheel
#   python -m twine upload dist/*
#
# For `development
# <https://pythonhosted.org/setuptools/setuptools.html#development-mode>`_:
#
#  ``pip install -e .``
#
# Packaging script
# ================
# Otherwise known as the evils of ``setup.py``.
#
# PyPA copied code
# ----------------
# From `PyPA's sample setup.py
# <https://github.com/pypa/sampleproject/blob/master/setup.py>`__,
# read ``long_description`` from a file. This code was last updated on
# 26-May-2015 based on `this commit
# <https://github.com/pypa/sampleproject/commit/4687e26c8a61e72ae401ec94fc1e5c0e17465b73>`_.
#
# Always prefer setuptools over distutils
from setuptools import setup
# To use a consistent encoding
from os import path
# Imports for `version parse code`_.
import sys
import os
import re

here = path.abspath(path.dirname(__file__))

# Get the long description from the relevant file.
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()
    # The inclusion of a raw tag causes `PyPI <http://pypi.python.org>`_ to not render the reST. Ouch. Remove it before uploading.
    long_description = re.sub('\.\. raw.*<\/iframe>', '', long_description, flags=re.DOTALL)

# This code was copied from `version parse code`_. See ``version`` in the call
# to ``setup`` below.
def read(*names, **kwargs):
    with open(
        os.path.join(os.path.dirname(__file__), *names),
        encoding=kwargs.get("encoding", "utf8")
    ) as fp:
        return fp.read()

def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")

# My code
# -------
# We support Python 3.4 and higher. I could instead use `python_requires <https://packaging.python.org/tutorials/distributing-packages/#python-requires>`_, but it seems like this is a new feature, so avoid it for now so that installs on older Python versions still work.
assert sys.version_info >= (3, 4)

setup(
    # This must comply with `PEP 0426
    # <http://legacy.python.org/dev/peps/pep-0426/#name>`_'s
    # name requirements.
    name='CodeChat',

    # Projects should comply with the `version scheme
    # <http://legacy.python.org/dev/peps/pep-0440/#public-version-identifiers>`_
    # specified in PEP440. I use this so that my Sphinx docs will have the same
    # version number. There are a lot of alternatives in `Single-sourcing the
    # Project Version
    # <https://packaging.python.org/en/latest/single_source_version.html>`_.
    # While I like something simple, such as ``import CodeChat`` then
    # ``version=CodeChat.__version__`` here, this means any dependeninces of
    # :doc:`__init__.py <CodeChat/__init__.py>` will be requred to run setup,
    # a bad thing. So, instead I read the file in ``setup.py`` and parse the
    # version with a regex (see `version parse code
    # <https://packaging.python.org/en/latest/single_source_version.html#single-sourcing-the-project-version>`_).
    version=find_version("CodeChat", "__init__.py"),

    description="The CodeChat system for software documentation",
    long_description=long_description,

    # The project's main homepage.
    url='http://codechat.readthedocs.io/en/latest/',

    author="Bryan A. Jones",
    author_email="bjones@ece.msstate.edu",

    license='GPLv3+',

    # These are taken from the `full list
    # <https://pypi.python.org/pypi?%3Aaction=list_classifiers>`_.
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: OS Independent',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Software Development :: Documentation',
        'Topic :: Text Processing :: Markup',
    ],

    keywords='literate programming',

    packages=['CodeChat'],

    # List run-time dependencies here.  These will be installed by pip when
    # your project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=([
        # Note: I don't include Sphinx in this list: while  :doc:`CodeToRest.py
        # <CodeChat/CodeToRest.py>` can be executed from the command line if the
        # packages below are installed, :doc:`CodeToRestSphinx.py
        # <CodeChat/CodeToRestSphinx.py>` can only be executed by Sphinx.
        'docutils>=0.13.1',
        'pygments>=2.1',
        'lxml']),

    # List additional groups of dependencies here (e.g. development
    # dependencies). You can install these using the following syntax,
    # for example:
    #
    #    ``$ pip install -e .[test]``
    extras_require={
        'test': ['pytest'],
    },

    # To package data files, I'm using ``include_package_data=True`` then
    # putting the files in :doc:`MANIFEST.in <MANIFEST.in>`. See `including data
    # files <http://pythonhosted.org/setuptools/setuptools.html#including-data-files>`_.
    include_package_data=True,
)
