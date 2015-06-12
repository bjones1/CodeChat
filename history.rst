.. Copyright (C) 2012-2015 Bryan A. Jones.

   This file is part of CodeChat.

   CodeChat is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

   CodeChat is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

   You should have received a copy of the GNU General Public License along with CodeChat.  If not, see <http://www.gnu.org/licenses/>.

*************************
History of recent changes
*************************
- Development version:

   - Update setup.py based on modern usage.
   - Update docs.
   - Add support for Sphinx v1.3. Process source files in memory, instead of creating ``.rst`` files. This allows source links to refer to the source code, not the intermediate ``.rst`` files.
   - Creation of a tutorial.
   - Support for all Sphinx themes.
   - Use of fenced code blocks to more cleanly include code in reST.
   - Support for Sphinx's conf.py ``highlight_language = 'python'``.
   - Improved CSS for better layout of paragraphs following code.
   - Support for block comments with or without indents.
   - Support for many more languages.
   - Simpler integration of CodeChat into a Sphinx conf.py.
   - Support for user-specified extensions.

- 0.0.18, 11-Feb-2015:

   - Remove unused PyQt dependencies.
   - Modernize documentation style in ``CodeChat/LanguageSpecificOptions``.

- 0.0.17, 17-Nov-2014:

   - Support Sphinx versions before 1.2.
   - Move non-CodeChat templates to Enki.

- 0.0.16 - 0.0.13, 11-Nov-2014:

   - Improved Sphinx template: doesn't replace default.css.
   - Updated CSS to work better with docutils.

- 0.0.12, released 1-Sep-2014:

   - Fixes so that CodeChat's Sphinx extension now works.
   - File encoding can now be specified.
   - Installaiton instructions added and docs reworked.

- 0.0.11, released 1-May-2014:

   - Fixed Unicode errors.
   - Removed incorrect extra spacing between code and comments.
   - Fixed unit tests and added a few more.
   - Removed unused CodeLink directive.

- 0.0.10, released 17-Apr-2014:

   - Revamped packaging.
   - Updated docs.
   - Used ``..`` instead of marker to indent comments, producing cleaner ReST.
   - Split ``CodeToRest`` into ``CodeToRest``, ``CodeToRestSphinx`` modules.
