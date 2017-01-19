# .. Copyright (C) 2012-2016 Bryan A. Jones.
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
# install dependencies from PyPI_, so use setuptools_. A source distribution is
# a good idea becaues it can run on a bare Python installation with no other
# installs required, but there's no standard format (.zip?, .tar.gz?, etc.). An
# .egg is nice, but requires setuptools/pip/ez_setup installed. The .whl
# (`Python wheel <http://wheel.readthedocs.org/en/latest/>`_)
# is the latest and greatest format that superceeds eggs, but with similar
# problems (requires wheel to be installed).
#
# Reading to get up to speed:
#
# * `Python Packaging User Guide <http://packaging.python.org/en/latest/>`_ -
#   the most up-to-date reference I've found so far. Tells which tools to
#   actually use.
#
# * `distutils <http://docs.python.org/distutils/index.html>`_ - The built-in
#   installer. Tells what to do, but not what actually happens. It doesn't have
#   the ability to install dependencies from `PyPI <http://pypi.python.org>`_,
#   which I need.
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
#   python setup.py sdist bdist_wheel
#   python -m twine upload dist\CodeChat-1.4.0*
#
# I can't get ``python setup.py upload`` to work. Of course, replace the version number in the command above.
#
# To `upload docs
# <http://pythonhosted.org/setuptools/setuptools.html#upload-docs-upload-package-documentation-to-pypi>`_,
# which are placed `here <http://pythonhosted.org/CodeChat/>`__
# (make sure to run Sphinx first, so the docs will be current):
#
#    ``python setup.py upload_docs --upload-dir=_build\html``
#
# For `development
# <https://pythonhosted.org/setuptools/setuptools.html#development-mode>`_:
#
#  ``python setup.py develop``
#
# Yajo helped `package this for Linux
# <https://build.opensuse.org/package/show/home:yajo:enki/python-codechat>`_.
# Thanks so much. See also :doc:`Linux_packaging/python-codechat.spec`.
# Unfortunately, the Linux packaging is untested.
#
# Packaging script
# ================
# Otherwise known as the evils of ``setup.py``.
#
# For users who install this from source but don't have setuptools installed,
# `auto-install it
# <https://pythonhosted.org/setuptools/setuptools.html#using-setuptools-without-bundling-it>`__.
# When packaging for Linux, downloads are blocked so we must specify a very old
# already-installed `version <http://pythonhosted.org/setuptools/history.html>`_.
# Leave this as a `patch
# <https://build.opensuse.org/package/view_file/home:yajo:enki/python-codechat/python-codechat.offline_setuptools.patch?expand=1>`_
# so that we normally use a more modern version.
import ez_setup
ez_setup.use_setuptools()
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
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path
# Imports for `version parse code`_.
import sys
import os
import re
import io

here = path.abspath(path.dirname(__file__))

# Get the long description from the relevant file.
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()
    # The inclusion of a raw tag causes PyPI_ to not render the reST. Ouch.
    # Remove it before uploading.
    long_description = re.sub('\.\. raw.*<\/iframe>', '', long_description, flags=re.DOTALL)

# This code was copied from `version parse code`_. See ``version`` in the call
# to ``setup`` below.
def read(*names, **kwargs):
    with io.open(
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
# We support Python 3.3 and higher.
assert sys.version_info >= (3, 3)

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
    url='https://pythonhosted.org/CodeChat/README.html',

    # Obscure my e-mail address to help defeat spam-bots.
    author="Bryan A. Jones",
    author_email="bjones AT ece.msstate.edu",

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
    #
    install_requires=(
      # `Enum <https://docs.python.org/3/library/enum.html>`_ was introduced in
      # Python 3.4. Use a backport of it if needed.
      (['enum34'] if sys.version_info.minor == 3 else [])
      # Note: I don't include Sphinx in this list: while  :doc:`CodeToRest.py
      # <CodeChat/CodeToRest.py>` can be executed from the command line if the
      # packages below are installed, :doc:`CodeToRestSphinx.py
      # <CodeChat/CodeToRestSphinx.py>` can only be executed by Sphinx.
      + ['docutils>=0.13.1',
         'pygments>=2.1']),

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
