# .. -*- coding: utf-8 -*-
#
#    Copyright (C) 2012-2013 Bryan A. Jones.
#
#    This file is part of CodeChat.
#
#    CodeChat is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#
#    CodeChat is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License along with CodeChat.  If not, see <http://www.gnu.org/licenses/>.
#
# ***********************************************************
# MultiprocessingSphinx.py - run Sphinx in a separate process
# ***********************************************************
#
# Imports
# =======
# These are listed in the order prescribed by `PEP 8 <http://www.python.org/dev/peps/pep-0008/#imports>`_.
#
# Standard library
# ----------------
import sys
import os
from multiprocessing import Process, Pipe, freeze_support
# Used to capture Sphinx's stderr output for display in the GUI.
from cStringIO import StringIO
#
# Third-party imports
# -------------------
# `Sphinx <http://sphinx.pocoo.org>`_ transforms `reST <http://docutils.sourceforge.net/docs/index.html>`_ to HTML, a core element of this tool.
import sphinx.cmdline

# MultiprocessingSphinxManager
# ============================
# This class starts and ends the process in which Sphinx runs.
class MultiprocessingSphinxManager(object):
    def __init__(self):
        # Start a process for background Sphinx operation
        freeze_support()
        self.parent_conn, self.child_conn = Pipe()
        self.process = Process(target = run_Sphinx_process, args = (self.child_conn, ))
        self.process.start()

    def finalize(self):
        self.parent_conn.close()
        self.process.join()

# PipeSendStdout
# ==============
# This class emulates stdout, transforming writes into a connection send. It's used by run_Sphinx_process_ below.
class PipeSendStdout(object):
    def __init__(self, conn):
        self.conn = conn

    def write(self, data):
        self.conn.send((False, data))

    def flush(self):
        pass

# run_Sphinx_process
# ==================
# This routine will be run in a separate process, performing Sphinx builds.
def run_Sphinx_process(conn):
    # Main loop
    while True:
        try:
            # Wait for data to use for invokation.
            (working_dir, html_dir) = conn.recv()
        except EOFError:
            # End this process if requested by a pipe close.
            return

        # First, capture stdout and stderr.
        old_stderr = sys.stderr
        sys.stderr = StringIO()
        old_stdout = sys.stdout
        sys.stdout = PipeSendStdout(conn)

        # Run Sphinx. The `command-line options <http://sphinx-doc.org/invocation.html>`_ are:
        os.chdir(working_dir)
        sphinx.cmdline.main( ('',
                              # Name of the Sphinx executable. Not needed here.
                              '-b', 'html',
                              # Select the HTML builder.
                              '-d', '_build/doctrees',
                              # Place doctrees in the _build directory; by default, Sphinx places this in _build/html/.doctrees.
                              '.',
                              # Source directory: the current directory.
                              html_dir) )
                              # Build directory: place the resulting HTML files in html_dir.

        # Send stdout, stderr data
        try:
            conn.send((True, sys.stderr.getvalue()))
            sys.stdout = old_stdout
            sys.stderr = old_stderr
        except EOFError:
            # End this process if requested by a pipe close.
            return
