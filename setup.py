# setup.py
# --------
# Builds and installs the CodeToRest portions of CodeChat.
#
# Copyright (c) 2012 Bryan A. Jones <bjones AT ece.msstate.edu>
#
# Packaging on Python is a mess, IMHO. Probably becase this is the first time
# I've done it. My understanding of the process so far:
#
# The built-in installer, `distutils <http://docs.python.org/distutils/index.html>`_,
# does quite a bit. However, it doesn't have the ability to install dependencies
# from `PyPi <http://pypi.python.org>`_, which I need.`setuptools
# <https://pythonhosted.org/setuptools> does, so I'm using that.
#
# For users who install this that don't have setuptools installed already (see
# https://pythonhosted.org/setuptools/setuptools.html#using-setuptools-without-bundling-it):
import ez_setup
ez_setup.use_setuptools()

from setuptools import setup, find_packages

setup(name = "CodeChat",
      version = '0.0.6',
      description = "The CodeChat system for software documentation",
      author = "Bryan A. Jones",
      author_email = "bjones AT ece.msstate.edu",
      license = "2-clause BSD",
      url = 'www.ece.msstate.edu/~bjones',
      classifiers = ['Development Status :: 3 - Alpha',
                     'Intended Audience :: Developers',
                     'License :: OSI Approved :: BSD License',
                     'Natural Language :: English',
                     'Programming Language :: Python',
                     'Topic :: Software Development :: Documentation',
                     'Topic :: Text Editors :: Documentation',
                     'Topic :: Text Processing :: Markup',
                     ],
      install_requires = ['Sphinx >= 1.1.0',
                          'Pygments >= 1.5',
                          ],
      py_modules = ['ez_setup',
                    'CodeChat.CodeToRest',
                    'CodeChat.CodeToRestSphinx',
                    'CodeChat.LanguageSpecificOptions'
                   ],
#      scripts = ['code_chat.py'],
      )
