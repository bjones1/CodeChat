*************************
History of recent changes
*************************
- Development version:

   - Update setup.py based on modern usage.
   - Update docs.
   - Add support for Sphinx v1.3. Process source files in memory, instead of creating ``.rst`` files. This allows source links to refer to the source code, not the intermediate ``.rst`` files.
   - Creation of a tutorial.
   - Support for all Sphinx themes.

- 0.0.18, 11-Feb-2015:

   - Remove unused PyQt dependencies.
   - Modernize documentation style in :doc:`CodeChat/LanguageSpecificOptions`.

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
