.. Copyright (C) 2012-2020 Bryan A. Jones.

    This file is part of CodeChat.

    CodeChat is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

    CodeChat is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along with CodeChat.  If not, see <http://www.gnu.org/licenses/>.

****************
Reference manual
****************
The manual presents links, whose targets give a full explanation of each concept.


Syntax
======
See the `style guide <CodeChat syntax>`.


Docutils
========
CodeChat adds the following role and directives to Docutils:

-   ``docname`` (a role): see `_docname_role`; in Sphinx, this is typically used via the ``|docname|`` substitution reference. See `docname substitution <docname substitution>`.
-   ``codeinclude``: see `_CodeInclude`.
-   ``fenced-code``: see `_FencedCodeBlock`. This is typically only needed for internal CodeChat use.
-   ``set-line``: See `_SetLine`. This is typically only needed for internal CodeChat use.


Sphinx
======
CodeChat provides the `../CodeChat/CodeToRestSphinx.py` extension. This extension provides the following configuration options:

-   `CodeChat_lexer_for_glob <CodeChat_lexer_for_glob>`


API
===
CodeChat provides the following API:

-   reStructuredText: `code_to_rest_string`, `code_to_rest_file`, `code_to_html_string`, and `code_to_html_file`.
-   Markdown: `code_to_markdown_string` and `code_to_markdown_file`.
-   Supporting routines: `get_lexer`.
-   Back-translation: the routines in `../CodeChat/RestToCode.py` are in beta.
