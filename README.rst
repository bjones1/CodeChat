===================================================================================
CodeChat
===================================================================================

Welcome to CodeChat, a conversational coding system.

Getting started
===============
To get up and running, you'll need to do some software installs. In addition to
the code in this package, you'll need

* Install `Python, v 2.7.2`_. I've compiled TRE extension for this version; it 
  probably won't work with Python v 3, but will probably work with Python 2.x.
* Install Sphinx, v 1.1.2. I haven't tested with any other version; I would expect that
  any 1.x version would work.
* Install PyQt 4.9.1. Older versions don't work.
* Install Pygments 1.4. I haven't tested with older versions.
* Install MiKTeX_ (optional, to generate math formulas viewable in this
  application). On the first run, you'll be prompted to install a few additional
  MiKTeX packages.

.. _MiKTeX: http://miktex.org/
.. _Python, v 2.7.2: http://www.python.org/download/releases/2.7.2/

Next, choose some source code to document. Currently, only C/C++, Python, and reST are supported.