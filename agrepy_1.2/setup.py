from distutils.core import setup, Extension

setup(name = "agrepy",
      version = 1.0,
      py_modules = ['agrepy'],
      ext_modules = [
        Extension('_agrepy', 
                  ['agrepy.i', 'agrepy.c', 'lagrepy.c', 'sagrepy.c'])])
