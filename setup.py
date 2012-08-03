# setup.py - Builds and installs the CodeChat distribution
#
# Copyright (c) 2012 Bryan A. Jones <bjones AT ece.msstate.edu>
#

from distutils.core import setup, Extension
import sys

data_files = []

if sys.platform == "win32":
    data_files = ["tre.dll"]

setup(name = "CodeChat",
      version = '0.0.0',
      description = "The CodeChat system for software documentation",
      long_description = open('README.txt').read(),
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
      requires = ['PyQt4 (>= 4.9.1)',
                  'Sphinx (>= 1.1.0)',
                  'Pygments (>= 1.5)',
                  ],
      packages = ['CodeChat'],
      data_files = data_files,
      ext_modules = [Extension("tre",
                               sources = ["tre/tre-python.c"],
                               include_dirs = ['tre'],
                               define_macros = [("HAVE_CONFIG_H", None)],
                               libraries = 'tre'
                               ),
                     ],
      )
