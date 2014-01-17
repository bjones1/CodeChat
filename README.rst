****************************************
CodeChat, a conversational coding system
****************************************
Welcome to CodeChat_, a conversational coding system. CodeChat encourages `literate programming <http://www.literateprogramming.com/>`_ by transforming source files into web pages and by providing a simple editor which synchronizes between the source code view and the web view of a document. Some examples of the results:

- Explaining to myself what my code should do helped me rewrite and fix `CodeToRest <https://dl.dropbox.com/u/2337351/CodeChat/doc/CodeChat/CodeToRest.py.html>`_.
- Likewise, explaining how a micro air vehicle responds to force created by its rotors enabled me to develop a `simulation of it <https://dl.dropbox.com/u/2337351/MAV_class/Python_tutorial/mav3d_simulation.py.html>`_.

For additional information, refer to :doc:`contents`.

Getting started
===============
First, download then run `Install_CodeChat.exe <https://dl.dropbox.com/u/2337351/CodeChat/Install_CodeChat.exe>`_ to install the program. Next, create a new CodeChat project by selecting ``File | Create new project`` and place it in a directory of your choosing, then follow the directions that appear. See `Running from source`_ for other options.

Optional modules
================
You may optionally install:

* `MiKTeX <http://miktex.org>`_ to generate math formulas viewable in this application. On the first run, you'll be prompted to install a few additional MiKTeX packages.
* `GraphViz <http://www.graphviz.org/>`_ to create graphs.

Recent changes
==============
- 17-Jan-2014:

  - Added a status bar to report build status, allowing the user to hide the build output window.
  - Fixed a code formatting bug that produces garbage in the HTML in some cases.
  - Added a timer to build after a short amount of idle time, rather than immediate builds.
  - Unnecessary double builds no longer occur.
  - Fixed a hang-on-close bug in Unix.
  - Included missing syntax highligher for many languages.
- 4-Nov-2013: Beta Doxygen support. Fixed crash when file with an unknown extension was loaded. Status bar now provides build results.
- 24-Apr-2013: Add ``.bat``, ``.ini``, and ``.iss`` as extensions recognized by CodeChat.
- 18-Apr-2013: Run Sphinx build in a separate process to provide a more responsive GUI.
- 3-Apr-2013: Fix to handle Unicode files correctly.
- Finally included the GPL license.
- Verbose Sphinx output is now displayed as the build progresses.
- The installer and executable should no longer trigger spurious virus warnings.
- The location in the web view is preserved even which a sync can't locate the corresponding position in the code view.
- Double-clicking on equations now searches for the underlying LaTeX source.
- Bug fixes: CodeChat no longer crashes when the last project directory is missing; the web view doesn't jump to the top when code under the cursor isn't found in the web view.
- Code and web views both open simultaneously; all edits are immediately compiled then synced.
- Improved home/end key behavior.
- Window title shows current project directory and open file.
- Added ``Create new project``, bug fixes.
- Added a window to show output from the Sphinx build process.
- Save/restore window geometry.
- Support for PHP, MATLAB files.
- Make matched text in browser/code views more visible.

Contributing
============
This is a fairly basic implementation; much improvement is needed! Please use the `issue tracker <http://bitbucket.org/bjones/documentation/issues?status=new&status=open>`_ to report bugs or request features; even better, or contribute to the code at the `CodeChat <https://bitbucket.org/bjones/documentation>`_ homepage!

Running from source
-------------------
You'll need Python 2.7 installed on your PC. Python 3 is definitely not supported; I haven't tried with earlier versions of Python.

Windows
^^^^^^^
- Download and install `PyQt4 <http://www.riverbankcomputing.com/software/pyqt/download>`_ and `Sphinx <http://sphinx-doc.org/>`_. Optionally install Miktex_ and Graphviz_.
- Build the TRE library using Visual Studio 2008 express (or the full version) based on the project file in ``tre-0.8.0-src/win32``.
- From a command line in ``tre-0.8.0-src/python``, run ``python setup.py build_ext -i -I../include`` then copy the resulting ``tre.pyd`` and ``tre.dll`` to the CodeChat root directory (where ``code_chat.py`` resides).
- Execute ``code_chat.py`` from the CodeChat root directory.

Unix
^^^^
The following was tested on Ubuntu 12.05 LTS. Modify as appropriate for your distribution.

To install::

 sudo apt-get install python-dev python-qt4 python-sphinx tortoisehg autoconf gettext libtool autopoint graphviz texlive
 hg clone https://bitbucket.org/bjones/documentation
 cd documentation/tre-0.8.0-src
 utils/autogen.sh
 ./configure
 make
 sudo make install
 cd python
 python setup.py build_ext -i
 cp tre.so ../..

To run::

 export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH
 ./code_chat.py

Mac
^^^
Sorry, I don't own one. I would hope the Unix approach above would provide a good starting place. Please contact me if you'd like to try this out.

License
=======
Copyright (C) 2012-2013 Bryan A. Jones.

This file is part of CodeChat.

CodeChat is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

CodeChat is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with CodeChat.  If not, see <http://www.gnu.org/licenses/>.
