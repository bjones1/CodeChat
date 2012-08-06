# setup.py
# --------
# Builds and installs the CodeChat distribution
#
# Copyright (c) 2012 Bryan A. Jones <bjones AT ece.msstate.edu>
#
# This only works for Windows -- Unix compiles of the tre library will need some patching.

# Packaging on Python is a mess, IMHO. Probably becase this is the first time I've done it. My understanding of the process so far:
#
# The built-in installer, `distutils <http://docs.python.org/distutils/index.html>`_, does quite a bit. However, it doesn't have the ability to install dependencies from `PyPi <http://pypi.python.org>`_, which I need. `Distribute <http://packages.python.org/distribute>`_ provides dependency installation in the `current state of packaging <http://guide.python-distribute.org/introduction.html#current-state-of-packaging>`_ (see also the fun graphic at the bottom of the `distribute page <http://packages.python.org/distribute/>`_).
#
# I two installation processes: end-users, which should be able to download and run a single Windows binary; then developers, which can ``easy_install CodeChat`` or ``pip install CodeChat``. Note that these require manual installation of Python 2.7 and PyQt to work. This script is only useful for creating a nice package for developers (I think).
#
# Things I've figured out: very little.
#
# Per the `docs <http://packages.python.org/distribute/setuptools.html#distributing-a-setuptools-based-project>`_, the two lines below allow use of this script even if setuptools aren't installed.
import distribute_setup
distribute_setup.use_setuptools()

from distutils.core import setup, Extension

setup(name = "CodeChat",
      version = '0.0.6',
      description = "The CodeChat system for software documentation",
      long_description = open('README.rst').read(),
      author = "Bryan A. Jones",
      author_email = "bjones AT ece.msstate.edu",
      license = "2-clause BSD",
      url = 'www.ece.msstate.edu/~bjones',
      classifiers = ['Development Status :: 3 - Alpha',
                     'Operating System :: Microsoft :: Windows',
                     'Intended Audience :: Developers',
                     'License :: OSI Approved :: BSD License',
                     'Natural Language :: English',
                     'Programming Language :: Python',
                     'Topic :: Software Development :: Documentation',
                     'Topic :: Text Editors :: Documentation',
                     'Topic :: Text Processing :: Markup',
                     ],
      # PyQt can't be easy_installed, so put it in the requires keyword, instead of install_requires.
      requires = ['PyQt (>= 4.9.1)'],
      install_requires = ['Sphinx >= 1.1.0',
                          'Pygments >= 1.5',
                          ],
      packages = ['CodeChat'],
      package_dir = {'CodeChat' : 'CodeChat'},
      package_data = {'CodeChat' : ['CodeChat.ui',
                                    'example/*',
                                    'Doc/*']},
      scripts = ['code_chat.py'],
      # tre.dll should be in the dame directory as its Python extension wrapper, tre.pyd. I don't know a good way to do this, so I used data_files.
      data_files = [('Lib/site_packages', ['tre.dll'])],
      ext_modules = [Extension("tre",
                               sources = ["tre/tre-python.c"],
                               include_dirs = ['tre'],
                               define_macros = [("HAVE_CONFIG_H", None)],
                               libraries = ['tre'],
                               library_dirs = ['tre'],
                               depends = ['tre/tre.h', 
                                          'tre/tre-config.h', 
                                         ],
                               ),
                     ],
      )
