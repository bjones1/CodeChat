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
# ***************************
# code_chat.py - Run CodeChat
# ***************************
# Author: Bryan A. Jones <bjones AT ece DOT msstate DOT edu>
#
# The :doc:`user manual <../README>` gives a broad overview of this system. In contrast, this document discusses the implementation specifics of the CodeChat system. In particular:
#
# .. contents:: Table of Contents
#    :local:
#
# CodeChat application
# ====================
# The application is comprised of the following modules. TODO: a block diagram of some sort here.
#
# .. toctree::
#    :maxdepth: 1
# 
#    CodeChat/CodeChat.py
#    CodeChat/CodeChatUtils.py
#    CodeChat/MultiprocessingSphinx.py
#    CodeChat/FindLongestMatchingString.py
#    CodeChat/CodeToRest.py
#    CodeChat/LanguageSpecificOptions.py
#    CodeChat/version.py
#    conf.py
#
#
# Unit testing
# ------------
# The following modules perform unit tests on portion of the application.
#
# .. toctree::
#    :maxdepth: 1
#
#    CodeChat/CodeChatUtils_test.py
#    CodeChat/FindLongestMatchingString_test.py
#    CodeChat/CodeToRest_test.py
#    CodeChat/pytest.ini
#
# Build system
# ============
# The build system provides the ability to package this program into a self-contained executable then publish it on the web. Core components:
#
# .. toctree::
#    :maxdepth: 1
#
#    build_exe.bat
#    pyinstaller_hooks/hook-CodeChat.py
#    build_dist.bat
#
# To do
# =====
# - Pre-process search text to convert images to alt text in web_to_code_sync:
#
#   - Create a list of (index, inserted alt text string length) to convert an index from the QTextEdit to an index in this text-only, images-replaced-as-alt-text version of the document.
# - Provide a styled preview: instead of styling only code, copy formatting from HTML version to plain text version using Scintilla's `styling <http://www.scintilla.org/ScintillaDoc.html#Styling>`_ feature. Basically, the code in the left view would have different font/size/color attributes, but be verbatim text. Any paragraph-level formatting (lists, indents, etc.) would be eventually handled by auto-word-wrap which makes the code look indented, etc, but not rely on any actual word-processor like formatting: the idea is to keep the code the same, just make it prettier. Perhaps have a toggle?
#
#   - One option is to throw away Scintilla's lexer for sytax coloring in favor of results copied from Pygments. This would be more consistent.
#   - One obvious problem: how to style text (comment characters, etc.) that doesn't appear in the HTML version? It's probably best not to style it at all, showing that it's syntax, not productive text.
#   - Use proportional text or not? Proportional provides a better preview, but makes some areas (getting title underline correct lengths) hard and others (working with tables) frustrating and nearly impossible.
#   - Implementation sketch: QTextEdit.document() gives a QTextDocument(). QTextDocument.begin() on this yields a QTextBlock; iterate using QTextBlock.next(). In each block, check QTextBlock.isValid(), then look at each QTextFragment in the block (QTextBlock.begin(); iterator.atEnd(), iterator.fragment().charFormat() use QTextBlock.text(), QTextBlock.charFormat().font() to get info. Given a fragment, get its index in the document then do an approximate match on it. Then, do a literal match on as much of the fragment as possible and style. Continue at the first non-matching location and repeat.
#   - Other ideas:
#
#     - Extend Sphinx' HTML formatter to output everything (all whitespace, backticks, etc.). This would probably be hard, since HTML also eats whitespace by default, enforces paragraph spacing, etc.
#     - Extend CodeToRest to wrap all reST syntax so that it appears verbatim in the output. This would probably be hard.
# - Rewrite documentation in this program. Make all the different title styles follow the `Python documentation standard <http://sphinx-doc.org/rest.html#sections>`_, with the following changes:
#
#   - Use ``@`` with overline for the title of the entire Sphinx output.
#   - Use ``*`` with overline for chapters. All .py files should contain a single chapter composed of the file name followed by a dash then explanatory text.
# - Preserve last cursor position in MRU list
# - Fix broken regexps for comments (#foo doesn't work)
# - Fix extensions in LanguageSpecificOptions
# - Create a short how-to video
# - Some way to display Sphinx errors then find the offending source line
# - Fix editor to render better HTML (long term -- probably QWebKit)
# - Port to Unix, Mac using CMake / CPack
# - Toolbars to insert common expressions (hyperlink, footnote, etc)
# - Optimization: have Sphinx read in doctrees, then stay in a reprocess loop, only writing results on close. Also, run Sphinx in a separate process using multiprocessing (which PyInstaller supports).
# - Provide a MRU list for projects. Have a unique file MRU list for each project.
# - Provide an options dialog (default font size, HTML dir name, etc.)
# - Use Doxygen output to auto-apply references to variables, classes, methods, etc.
#
# Run CodeChat
# ============
# This script runs the CodeChat application.
#
# This script will be imported by the main entry point, then again by the multiprocessing module. So, only put imports below needed by both.
from CodeChat.MultiprocessingSphinx import MultiprocessingSphinxManager

if __name__ == '__main__':
    # Hide this import, so the MultiprocessingSphinx process doesn't import unnecessary items.
    from CodeChat.CodeChat import main

    msm = MultiprocessingSphinxManager()
    main(msm)
