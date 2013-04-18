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
# *****************
# CodeChat_utils.py
# *****************
#
# Imports
# =======
# These are listed in the order prescribed by `PEP 8 <http://www.python.org/dev/peps/pep-0008/#imports>`_.
#
# Standard library
# ----------------
import sys
import os
from multiprocessing import Process, Pipe
# Used to capture Sphinx's stderr output for display in the GUI.
from cStringIO import StringIO
#
# Third-party imports
# -------------------
# `Sphinx <http://sphinx.pocoo.org>`_ transforms `reST <http://docutils.sourceforge.net/docs/index.html>`_ to HTML, a core element of this tool.
import sphinx.cmdline


parent_conn = None
process = None
def init_multiprocessing():
    global parent_conn, process
    # Start a process for background Sphinx operation
    parent_conn, child_conn = Pipe()
    process = Process(target = run_Sphinx_process, args = (child_conn, ))
    process.start()

def end_multiprocessing():
    global parent_conn, process
    print('Sending shutdown...')
    parent_conn.close()
    print('Joining...')
    process.join()
    print('Done.')

def run_Sphinx_process(conn):
    while True:
        try:
            print('Waiting for data...')
            (working_dir, html_dir) = conn.recv()
            print('Got %s, %s. Sending response...' % (working_dir, html_dir))
            conn.send([True, 'donee'])
        except EOFError:
            return
    return

    # Main loop
    while True:
        try:
            # Wait for data to use for invokation.
            (working_dir, html_dir) = conn.recv()
        except EOFError:
            # End this process if requested.
            return

        # First, capture stdout and stderr.
        sys.stderr = StringIO()
        sys.stdout = StringIO()

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
            conn.write((False, sys.stdout.getvalue()))
            conn.write((True, sys.stderr.getvalue()))
        except EOFError:
            # End this process if requested.
            return
