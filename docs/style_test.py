# .. Copyright (C) 2012-2020 Bryan A. Jones.
#
#    This file is part of CodeChat.
#
#    CodeChat is free software: you can redistribute it and/or modify it under
#    the terms of the GNU General Public License as published by the Free
#    Software Foundation, either version 3 of the License, or (at your option)
#    any later version.
#
#    CodeChat is distributed in the hope that it will be useful, but WITHOUT ANY
#    WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#    FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
#    details.
#
#    You should have received a copy of the GNU General Public License along
#    with CodeChat.  If not, see <http://www.gnu.org/licenses/>.
#
# **************************************
# |docname| - Styling tests for CodeChat
# **************************************
# This file contains no useful code, but serves as a test bed to make sure code to comment transitions are styled correctly.
#
# `Disable Black <https://github.com/psf/black#the-black-code-style>`_ for this block.
# fmt: off
#
# The syntax below prevents some linter complaints.
to_code = None
def to_indented_code(): pass


# Docstrings
# ==========
def foo():
    """A function that
       checks if docstrings are dedented **properly**.

       Check that multiple paragraphs work.

        Check that indents (even this small one) work."""
    pass


# All reST types
# ==============
# Here are all the reST body elements, tested with intermingled code to check code to text back to code, following the order given in the `reStructuredText Markup Specification <http://docutils.sourceforge.net/docs/ref/rst/restructuredtext.html>`_.
#
# Sections
# --------
if to_code:
# and back
# ^^^^^^^^
#
# Sections
# ^^^^^^^^
    to_indented_code()
# and back
# ^^^^^^^^
# Note that sections shouldn't be indented, so they're not tested here.

#
# Transitions
# -----------
# A transition
#
# ----
if to_code:
# ----
#
# and back.

# A transition
#
# ----
    to_indented_code()
# ----
#
# and back.

    # An indented transition
    #
    # ----
if to_code:
    # ----
    #
    # and back.

    # An indented transition
    #
    # ----
        to_indented_code()
    # ----
    #
    # and back.

#
# Paragraphs
# ----------
# A plain paragraph
if to_code:
# then back.

# A plain paragraph
    to_indented_code()
# then back.

    # An indented paragraph
if to_code:
    # then back.

    # An indented paragraph
        to_indented_code()
    # then back.

#
# Bulleted lists
# --------------
# - A bulleted list
if to_code:
# - and back.

# - A bulleted list
    to_indented_code()
# - and back.

    # - An indented bulleted list
if to_code:
    # - and back.

    # - An indented bulleted list
        to_indented_code()
    # - and back.

#
# #.    Enumerated lists
if to_code:
# #.    and back.

# #.    Enumerated lists
    to_indented_code()
# #.    and back.

    # #.    An indented enumerated list
if to_code:
    # #.    and back.

    # #.    An indented enumerated lists
        to_indented_code()
    # #.    and back.

#
# Definition lists
# ----------------
# A definition
#   list
if to_code:
# and
#   back.

# A definition
#   list
    to_indented_code()
# and
#   back.

    # An indented definition
    #   list
if to_code:
    # and
    #   back.

    # An indented definition
    #   list
        to_indented_code()
    # and
    #   back.

#
# Field lists
# -----------
# :A: field list
if to_code:
# :and: back.

# :A: field list
    to_indented_code()
# :and: back.

    # :An indented: field list
if to_code:
    # :and: back.

    # :An: indented field list
        to_indented_code()
    # :and: back.

#
# Option lists
# ------------
# -An   option list
if to_code:
# -And  back

# -An   option list
    to_indented_code()
# -And  back

    # -An   indented option list
if to_code:
    # -And  back.

    # -An   indented option list
        to_indented_code()
    # -And  back.

#
# Literal blocks
# --------------
# Testing is a bit tricky, since the styling is very close to code already.
#
# ::
#
#    A literal block
if to_code:
# ::
#
#   and back.

# ::
#
#    A literal block
    to_indented_code()
# ::
#
#   and back.

    # ::
    #
    #   An indented literal block
if to_code:
    # ::
    #
    #   and back.

    # ::
    #
    #   An indented literal block
        to_indented_code()
    # ::
    #
    #   and back.

# Per-line quoting::
#
# > for a literal block
if to_code:
# and::
#
# > back.

# Per-line quoting::
#
# > for a literal block
    to_indented_code()
# and::
#
# > back.

    # Per-line quoting::
    #
    # > for an indented literal block
if to_code:
    # and::
    #
    # > back.

    # Per-line quoting::
    #
    # > for an indented literal block
        to_indented_code()
    # and::
    #
    # > back.

#
# Line blocks
# -----------
# | line
# | blocks
if to_code:
# | and
# | back.

# | line
# | blocks
    to_indented_code()
# | and
# | back.

    # | indented line
    # | blocks
if to_code:
    # | and
    # | back.

    # | indented line
    # | blocks
        to_indented_code()
    # | and
    # | back.

#
# Doctest blocks
# --------------
# >>> Doctest_blocks
if to_code:
# >>> and_back

# >>> Doctest_blocks
    to_indented_code()
# >>> and_back

    # >>> Indented_doctest_blocks
if to_code:
    # >>> and_back

    # >>> Indented_doctest_blocks
        to_indented_code()
    # >>> and_back

#
# Tables
# ------
# = =====
# A Table
# = =====
# 1 two
# = =====
if to_code:
# ===   ====
# and   back
# ===   ====
# 1     two
# ===   ====

# = =====
# A Table
# = =====
# 1 two
# = =====
    to_indented_code()
# ===   ====
# and   back
# ===   ====
# 1     two
# ===   ====

    # ==    ==============
    # An    indented table
    # ==    ==============
    # 1     two
    # ==    ==============
if to_code:
    # ===   ====
    # and   back
    # ===   ====
    # 1     two
    # ===   ====

    # ==    ==============
    # An    indented table
    # ==    ==============
    # 1     two
    # ==    ==============
        to_indented_code()
    # ===   ====
    # and   back
    # ===   ====
    # 1     two
    # ===   ====

#
# Directives
# ==========
# Test some directives, following the order in the `reStructuredText Directives <http://docutils.sourceforge.net/docs/ref/rst/directives.html>`_ document.
#
# `Admonitions <http://docutils.sourceforge.net/docs/ref/rst/directives.html#admonitions>`_
# -----------------------------------------------------------------------------------------
# Attention
# ^^^^^^^^^
# .. attention:: An attention directive
if to_code:
# .. attention:: and back.

# .. attention:: An attention directive
    to_indented_code()
# .. attention:: and back.

    # .. attention:: An indented attention directive
if to_code:
    # .. attention:: and back.

    # .. attention:: An indented attention directive
        to_indented_code()
    # .. attention:: and back.

#
# contents
# ^^^^^^^^
# .. contents:: A table of contents
#   :depth: 1
if to_code:
# .. contents:: and back.
#   :depth: 1

# .. contents:: A table of contents
#   :depth: 1
    to_indented_code()
# .. contents:: and back.
#   :depth: 1

    # .. contents:: An indented table of contents
    #   :depth: 1
if to_code:
    # .. contents:: and back.
    #   :depth: 1

    # .. contents:: An indented table of contents
    #   :depth: 1
        to_indented_code()
    # .. contents:: and back.
    #   :depth: 1

#
# Nested body elements
# ====================
# Test the behavior of nesting elements, making sure all margins get set properly.
#
# One
#
#   Two
#
#   -   Three
#
#       #.  Four
#
#           Five
#               six
#
#               :Seven: eight
#
#                   -Nine   ten
#
#                       | eleven
#                       | twelve
to_code
# and back.
#
# I don't know that more nesting really does any more testing.
