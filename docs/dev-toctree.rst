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
   ../CodeChat/RestToCode.py
   ../CodeChat/CodeToRestSphinx.py
   ../CodeChat/CommentDelimiterInfo.py
   ../.gitignore
   ../.flake8

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
   ../codechat_config.json


Packaging
=========
.. toctree::
   :maxdepth: 1

   ../setup.py
   ../MANIFEST.in
