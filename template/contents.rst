Template for a project using CodeChat
=====================================
This file provides a template for your new CodeChat project and gives directions on how to use the application, and provides examples of its use. A quick start:

#. To view this document as a web page, press ``Ctrl-G`` or double-click on any word in this document. Your code will be transformed to HTML and the program will now show the word and its surroundings highlighed in the browser view. Status messages from the build appear in the bottom pane. For a more accurate rendering of the web page, select ``View | In browser``.
#. Now that you're in web view, double-click on text you'd like to edit: for example, **delete me**. This will move to the same location in the code view. Edit and repeat these two steps. The syntax you see is `reST markup <https://dl.dropbox.com/u/2337351/rst-cheatsheet.html>`_ by `Sphinx <http://sphinx-doc.org/>`_. The items on the ``Help`` menu provide a convenient reference.

Now, you're ready to document some code. Open :doc:`conf.py` for an example of this process. When you're ready to document your own code:

#. Add your source files to the table of contents below, after ``conf.py``, then save.
#. Open one of your source files and begin documenting; all comments [#]_ are processed as reST/Sphinx, while source code will be syntax hilighted.

.. [#] Currently, only single-line C/C++, Python, reST, assembly (.s), BASH scripts, PHP, and MATLAB scripts are supported. 

Table of Contents
-----------------
.. toctree::
   :maxdepth: 2

   conf.py

Indices and tables
------------------
* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
