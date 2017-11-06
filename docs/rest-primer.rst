.. Copyright (C) 2012-2016 Bryan A. Jones.

    This file is part of CodeChat.

    CodeChat is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

    CodeChat is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along with CodeChat.  If not, see <http://www.gnu.org/licenses/>.

reStructuredText Primer
=======================
This is a simplified version of the excellent `Sphinx reStructuredText Primer <http://sphinx-doc.org/rest.html>`_.

Inline markup
-------------
The standard reST inline markup is quite simple: *emphasis (italics)*, **strong emphasis (boldface)**, and ``code samples``.

Lists and Quote-like blocks
---------------------------
* This is a bulleted list.
* It has two items, the second
  item uses two lines.

1. This is a numbered list.
2. It has two items too.

reST can autonumber lists:

#. This is a numbered list.
#. It has two items too.


   Quoted paragraphs are created by just indenting them more than the surrounding paragraphs.

Line blocks are a way of preserving line breaks:

   | These lines are
   | broken exactly like in
   | the source file.

Source Code
-----------
Literal code blocks are introduced by ending a paragraph with the special marker::

   void foo(int bar) {
      return bar
   }

Tables
------
Two forms of tables are supported: *Grid tables* like this:

   +------------------------+------------+----------+----------+
   | Header row, column 1   | Header 2   | Header 3 | Header 4 |
   | (header rows optional) |            |          |          |
   +========================+============+==========+==========+
   | body row 1, column 1   | column 2   | column 3 | column 4 |
   +------------------------+------------+----------+----------+
   | body row 2             | ...        | ...      |          |
   +------------------------+------------+----------+----------+

...and *simple tables* like this:

   =====  =====  =======
   A      B      A and B
   =====  =====  =======
   False  False  False
   True   False  False
   False  True   False
   True   True   True
   =====  =====  =======

.. _a label:

Hyperlinks
----------
Use `link text <http://example.com/>`_ for inline web links. Or, refer to `a label`_.

Sections
--------
Section headers are created by underlining (and optionally overlining) the section title with a punctuation character, at least as long as the text.

Images
------
reST supports an image directive:

.. image:: gnu.png

Gotchas
-------
There are some problems one commonly runs into while authoring reST documents:

* **Separation of inline markup:** Inline markup spans must be separated from the surrounding text by non-word characters; you have to use a backslash-escaped space to get around that. For example, H\ :sub:`2`\ O, not H:sub:`2`O.

* **No nested inline markup:** Something like *H\ :sub:`2`\ O* is not possible.

