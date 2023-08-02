***********************
Developer documentation
***********************

Core code
=========
.. toctree::
   :maxdepth: 1

   ../CodeChat/__init__.py
   ../CodeChat/SourceClassifier.py
   ../CodeChat/CodeToRest.py
   ../CodeChat/CodeToMarkdown.py
   ../CodeChat/CodeToPretext.py
   ../CodeChat/RestToCode.py
   ../CodeChat/CodeToRestSphinx.py
   ../CodeChat/mdbook_CodeChat.py
   ../CodeChat/CommentDelimiterInfo.py
   ../CodeChat/css/__init__.py
   ../.gitignore
   ../.flake8
   ../pyproject.toml


Style sheets
============
This section presents the style sheets used for CodeChat webpages.

.. toctree::
   :maxdepth: 1

   ../CodeChat/css/CodeChat.css
   ../CodeChat/css/CodeChat_sphinx_rtd_theme.css
   ../CodeChat/css/docutils.css


Testing
=======
To run the tests, execute ``pytest test`` from the root directory of the project.

.. toctree::
   :maxdepth: 1
   :glob:

   ../test/*.py
   ../.travis.yml
   ../appveyor.yml
   ../docs/style_test.py


Documentation generation
========================
To build the documentation, execute ``sphinx-build -d _build/doctrees . _build`` from the root directory of the project.

.. toctree::
   :maxdepth: 1

   ../conf.py
   ../readthedocs.yml
   ../codechat_config.yaml


Packaging
=========
.. toctree::
   :maxdepth: 1

   ../setup.py
   ../setup.cfg
   ../MANIFEST.in


Ideas / todo items
==================
-  Implement caching and correct styling for `../CodeChat/mdbook_CodeChat.py`.
-  Introduce a new directive such as ``code-ref`` that allows referencing names in the code. Use `ctags <https://docs.ctags.io/en/latest/index.html>`_ to generate these references.

   -  Perhaps ``:code-ref:`optional-source-file.ext::scope-0::scope-1::...::scope-n <optional name>```.

   -  Provide an output-independent function to run ctags on a list of source files, then read the tags into a data structure:

      .. code::

         Dict[
            # A relative path to the source file.
            str,
            # A dict of names in this source file.
            Dict[
               # Include both all names in the top-level scope plus any
               # non-conflicting name in a lower scope. That is, given a
               # variable named ``foo::bar``, this dict would contain both
               # ``foo`` as the top-level scope and ``bar``, unless there
               # was another variable named ``zot::bar`` in the same file
               # (meaning that ``bar`` isn't a unique name).
               str,
               # Information about this name:
               Tuple[
                  # The line number where this name was defined.
                  int,
                  # If this name defines a scope containing more names,
                  # this contains them, again as a ``Dict[int, Optional
                  # [Dict]]``.
                  Optional[Dict]]]]

   -  Provide per-output ways to embed this in the output.
   -  Profile this to see what's slow.