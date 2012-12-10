CodeChat, a conversational coding system
========================================

Welcome to CodeChat_, a conversational coding system. CodeChat encourages `literate programming <http://www.literateprogramming.com/>`_ by transforming source files into web pages and by providing a simple editor which synchronizes between the source code view and the web view of a document. Some examples of the results:

* Explaining to myself what my code should do helped me rewrite and fix `CodeToRest <https://dl.dropbox.com/u/2337351/CodeChat/doc/CodeChat/CodeToRest.py.html>`_.
* Likewise, explaining how a micro air vehicle responds to force created by its rotors enabled me to develop a `simulation of it <https://dl.dropbox.com/u/2337351/MAV_class/Python_tutorial/mav3d_simulation.py.html>`_.

Getting started
---------------
First, download then run `Install_CodeChat.exe <https://dl.dropbox.com/u/2337351/CodeChat/Install_CodeChat.exe>`_ to install the program. To create a new CodeChat project:

#. Copy the files from ``<path to CodeChat>/template`` to a directory of your choosing.
#. Switch to the CodeChat application, then choose ``File | Choose project dir`` and select the directory you chose above.
#. Choose ``File | Open`` then open ``contents.rst``. Add your source files to the list in that document.
#. Open one of your source files and begin documenting; all comments [#]_ are processed as `reST markup <https://dl.dropbox.com/u/2337351/rst-cheatsheet.html>`_ by `Sphinx <http://sphinx-doc.org/>`_. The source files in ``<path to CodeChat>/src`` provide many examples of the use of this system. The items on the ``Help`` menu provide a convenient reference to the syntax used.
#. To view the results, select ``View | Toggle pane`` to view your code as a web page; for a more accurate rendering, select ``View | In browser``. Note that CodeChat will hilight the line in the web view on which your cursor was positioned in the code view.
#. While in web view, click on text you'd like to edit then select ``View | Toggle pane`` to move to the code view. Edit and repeat steps 4-6 above.

.. [#] Currently, only C/C++, Python, and reST are supported. 

Optional modules
----------------
You may optionally install:

* `MiKTeX <http://miktex.org>`_ to generate math formulas viewable in this application. On the first run, you'll be prompted to install a few additional MiKTeX packages.
* `GraphViz <http://www.graphviz.org/>`_ to create graphs.

Contributing
------------
This is a fairly basic implmentation; much improvement is needed! Please report bugs, request features, or contribute to the code at the homepage for CodeChat_.

.. _CodeChat: https://bitbucket.org/bjones/documentation