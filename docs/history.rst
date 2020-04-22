.. Copyright (C) 2012-2020 Bryan A. Jones.

    This file is part of CodeChat.

    CodeChat is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

    CodeChat is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along with CodeChat.  If not, see <http://www.gnu.org/licenses/>.


******************
History of changes
******************
-   `Github master <https://github.com/bjones1/CodeChat>`_:

    -   No changes yet.

-   1.8.0, 22-Apr-2020:

    -   Updates to be compatible with Pygments 2.6.
    -   Documentation improvements.
    -   Remove spacing between code and comments using CSS classes.
    -   Moved the Sphinx template to ``CodeChat/sphinx_template`` and CSS files to ``CodeChat/css``.
    -   Changed the Sphinx template ``conf.py`` to include CodeChat's ``css`` directory in ``html_static_path``. **Warning**: after updating to this version, you must edit all ``conf.py`` files to incorporate this change and delete the copied ``CodeChat.css`` files. The necessary changes are:

        At the top of ``conf.py``:

        .. code::

            import CodeChat.CodeToRest

        In the body of ``conf.py``:

        .. code::

            html_static_path = CodeChat.CodeToRest.html_static_path()

-   1.7.3, 9-Feb-2020:

    -   Added support for `Thrift <https://thrift.apache.org/>`_.
    -   Added support for HTML+Django/Jinja.
    -   Added support for Sphinx 2.4.0.
    -   Added support for Markdown in source files. See `style_guide.md.cpp`.

-   1.7.2, 18-Oct-2019:

    -   Fixes to enable builds on `ReadTheDocs <https://readthedocs.org/>`_.

-   1.7.1, 18-Oct-2019:

    -   Support MATLAB ``...`` and ``%`` comments, AppleScript ``--`` and ``#`` comments, and PHP ``#`` and ``//`` comments.
    -   Correctly recognize COBOL comments.
    -   Define the inline comment delimiter as a sequence of strings, instead of a single string.

-   1.7.0, 9-Apr-2019:

    -   Corrected the link to the GPL license.
    -   Move CSS files out of the template project's ``index.rst``.
    -   Update to Sphinx 2.0; drop support for older Sphinx versions.
    -   Remove unnecessary ``CodeChat_excludes`` configuration variable. Any files in ``html_static_path`` are automatically excluded from the build starting in Sphinx 1.8, so this setting no longer applies.

-   1.6.1, 25-Sep-2018:

    -   Updates to work with Sphinx 1.8.
    -   Use consistent matching for ``CodeChat_lexer_for_glob``.
    -   Various bits of code cleanup.

-   1.6.0, 3-Aug-2018:

    -   Refactor code: separate source code classifier from reST output.
    -   Add support for Markdown.
    -   Tested to work with Sphinx 1.7.
    -   Add the `codeinclude <_CodeInclude>` directive.
    -   Provide default destination filenames for ``code_to_xxx_file`` functions.
    -   Add the `reference_manual`.

-   1.5.9, 10-Nov-2017

    -   Update and clean up docs.
    -   Add the ``|docname|`` substitution definition and `underlying role <_docname_role>`.
    -   Place minimum Sphinx version requirement only in `../CodeChat/CodeToRest.py`; remove it from `../conf.py`.

-   1.5.8, 8-Nov-2017

    -   Update minimum required Sphinx version to 1.5.
    -   Turn show source option on by default.
    -   Fix duplicate extensions on source files.
    -   Update style guide for improved formatting introduced in v1.5.0.

-   1.5.7, 6-Nov-2017

    -   Fixed auto-generated ``.. highlight`` directive to use correct name.
    -   Fixed CSS for the ReadTheDocs_ theme.

-   1.5.6, 31-Oct-2017

    -   Fixed styles for use with Docutils.

-   1.5.5, 18-Oct-2017

    -   Automatically insert a ``.. highlight`` directive based on the lexer used, unless the file contains `file-wide metadata <http://www.sphinx-doc.org/en/stable/markup/misc.html#file-wide-metadata>`_.

-   1.5.4, 29-Sep-2017

    -   Update template CSS to latest.

-   1.5.3, 29-Sep-2017

    -   CSS fixes to work with all built-in Sphinx styles.

-   1.5.2, 29-Sep-2017

    -   More CSS formatting improvements; added a test page.
    -   Remove Linux packaging, since it's out of date.

-   1.5.1, 27-Sep-2017

    -   Improved CSS formatting.
    -   Docs now hosted on readthedocs.

-   1.5.0, 27-Sep-2017

    -   Added MXML and 15 C-like languages.
    -   Consistent treatment of path in globs stored in ``CodeChat_lexer_for_glob``.
    -   Better error messages for incorrect lexers specified in ``CodeChat_lexer_for_glob``.
    -   CI fixes.
    -   Better feedback of parse errors in Python source.
    -   Added support for translating HTML to reST.
    -   Improved CSS formatting.

-   1.4.1, 19-Jan-2017

    -   Updated code to work with docutils 0.13.1. This breaks older docutils.
    -   Provided a ``is_source_code`` function in ``CodeToRestSphinx``.
    -   Corrected the ``set-line`` directive to properly renumber all lines.

-   1.4.0, 22-Nov-2016:

    -   More languages tested, along with some fixes.
    -   Python docstrings are now processed as reST.
    -   Added the ``CodeChat_excludes`` configuration variable.

-   1.3.1, 29-Apr-2016:

    -   Installer fixes.
    -   CI testing added.
    -   Test more languages.

-   1.3.0, 19-Mar-2016:

    -   Ported to Python 3.
    -   Added NSIS, Spec file support.
    -   Tests now reside in a separate ``test/`` subdirectory.
    -   Documentation fixes.

-   1.2.1, 12-Nov-2015:

    -   Fixed broken hyperlinks in the `tutorial-examples`.
    -   Provide correct Linux installation instructions.
    -   Correctly report the line number of errors.

-   1.2.0, 12-Nov-2015:

    -   Prevent errors when an indented comment follows code.
    -   Display the correct line number of errors/warnings.
    -   Document brokenness when headings are indented.

-   1.1.1, 11-Nov-2015:

    -   Fix to actually support ``SConscript`` and ``Makefiles``.

-   1.1.0, 10-Nov-2015:

    -   Dropped support for pre-v1.3 Sphinx.
    -   The extension of source files is now preserved, rather than being stripped. This makes for a simpler ``conf.py``, since ``source_suffix`` is no longer modified.
    -   The correct HTML extension is now written to ``sphinx-enki-info.txt``.
    -   A link to install instructions is now provided in `../README`.
    -   The ``.ini`` file format is now supported.
    -   ``SConscript`` and ``Makefiles`` are now supported.

-   1.0.1, 21-Aug-2015:

    -   Support MATLAB (``.m``) files.
    -   Provide a tutorial in the docs.

-   1.0.0, 20-Jul-2015:

    -   Update ``setup.py`` based on modern usage.
    -   Update docs.
    -   Add support for Sphinx v1.3. Process source files in memory, instead of creating ``.rst`` files. This allows source links to refer to the source code, not the intermediate ``.rst`` files.
    -   Creation of a tutorial.
    -   Support for all Sphinx themes.
    -   Use of fenced code blocks to more cleanly include code in reST.
    -   Support for Sphinx's conf.py ``highlight_language = 'python'``.
    -   Improved CSS for better layout of paragraphs following code.
    -   Support for block comments with or without indents.
    -   Support for many more languages.
    -   Simpler integration of CodeChat into a Sphinx ``conf.py``.
    -   Support for user-specified extensions.
    -   Support for indented headings; note that they won't be indented in the resulting HTML.
    -   Whitespace is removed in auto-save and build mode.
    -   Errors and warnings are now displayed in the Preview dock's status bar, which replaces the useless progress bar.
    -   Avoid double builds when in auto-save and build mode.
    -   Template project now include ``conf.py`` and ``CodeChat.css``.

-   0.0.18, 11-Feb-2015:

    -   Remove unused PyQt dependencies.
    -   Modernize documentation style in ``CodeChat/LanguageSpecificOptions``.

-   0.0.17, 17-Nov-2014:

    -   Support Sphinx versions before 1.2.
    -   Move non-CodeChat templates to Enki.

-   0.0.16 - 0.0.13, 11-Nov-2014:

    -   Improved Sphinx template: doesn't replace default.css.
    -   Updated CSS to work better with docutils.

-   0.0.12, released 1-Sep-2014:

    -   Fixes so that CodeChat's Sphinx extension now works.
    -   File encoding can now be specified.
    -   Installation instructions added and docs reworked.

-   0.0.11, released 1-May-2014:

    -   Fixed Unicode errors.
    -   Removed incorrect extra spacing between code and comments.
    -   Fixed unit tests and added a few more.
    -   Removed unused CodeLink directive.

-   0.0.10, released 17-Apr-2014:

    -   Revamped packaging.
    -   Updated docs.
    -   Used ``..`` instead of marker to indent comments, producing cleaner ReST.
    -   Split ``CodeToRest`` into ``CodeToRest``, ``CodeToRestSphinx`` modules.

-   Previous versions lack release notes.


********************
Ideas for the future
********************
-   Update `../setup.py` to use a ``setup.cfg`` file.
-   Update Travis OS X tests.
-   Testing:

    -   For Sphinx.
    -   For ``code_to_xxx_file`` functions.
    -   For the directives and role in `../CodeChat/CodeToRest.py`.
