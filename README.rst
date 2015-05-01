*****************************
A programmer's word processor
*****************************

`CodeChat <https://bitbucket.org/bjones/documentation/overview>`_ transforms source code into a web page, allowing developers to view their program as a beautiful and descriptive document by adding headings, formatting, hyperlinks, diagrams, images, and other forms of rich content to capture the ideas and insights that naturally flow from the process of writing a program. It also provides a blank slate in which to plan ahead, by sketching out an algorithm before committing it to code or laying out a design document which can evolve as the code does. This `literate programming <http://www.literateprogramming.com/>`_ paradigm changes the way developers think by intermingling ideas with their implementation as code, dramatically improving a programmer’s abilities.

.. contents:: Contents
   :local:

Tutorial
========
This tutorial shows how the `Enki <http://enki-editor.org/>`_ text editor, integrated with the CodeChat_ literate programming plug-in, provides a powerful environment for creating expressive programs. Or, take a look at some examples_ to see this ideas in action.

Basic restructuredText
----------------------
CodeChat relies on `reStructuredText <http://docutils.sourceforge.net/rst.html>`_ (`reST <http://docutils.sourceforge.net/rst.html>`_) in comments to provide human-readable markup. "ReStructuredText is an easy-to-read, what-you-see-is-what-you-get plaintext markup syntax" [#]_. So, this tutorial beings by exploring reST using Enki.

First, install Enki_, which hosts the CodeChat_ system. Next, download the `source code for CodeChat <https://bitbucket.org/bjones/documentation/downloads>`_, then unzip this in a directory of your choice. Now, open the source for this document, ``<location of unzipped CodeChat files>/README.rst``, in Enki. Move around the document, noticing that the text and web view are automatically synchronized. Click on any element of the web view to show the corresponding text view. Edit -- your changes are visible immediately. Note that the syncronization ability applies to any file Enki can preview, such as HTML files (try ``<location of unzipped CodeChat files>/CodeChat/LICENSE.html``, for exampe, or Enki's `README.md <https://raw.githubusercontent.com/hlamer/enki/master/README.md>`_).

Now, explore creating your own reST file: create a new file, then save it with an extension of ``.rst``. Based on the very helpful `reST primer <http://sphinx-doc.org/rest.html>`_, try out some syntax: create headings, include a hyperlink, add an image, use inline markup. When errors occur, they are reported in the log window and typically in-line in the resulting web page. When a page is complete, the save icon in the preview window stores the resulting HTML to disk.

By design, reST operates on one file at a time. To create a web site consisting of multiple, interlinked documents, we turn to Sphinx, wihch adds this ability to reStructuredText.

.. [#] http://docutils.sourceforge.net/rst.html

Basic Sphinx_
-------------
"`Sphinx <http://sphinx-doc.org/index.html>`_ is a tool that makes it easy to create intelligent and beautiful documentation" [#]_. It provides additional features lacking basic restructuredText, including the ability to link together many documents (such as all the files in a program's source code).

To use Sphinx with Enki_, first go to ``Settings | Settings | Sphinx``. Then enable Sphinx and select ``<location of unzipped CodeChat files>`` as the project directory. Click OK. Then, open ``<location of unzipped CodeChat files>/README.rst``, or switch to it if it's still open. The resulting web page will be displayed in the Preview dock.

In addition to providing a number of beautiful themes for rendering reST files, Sphinx creates a set of linked documents. To see this in action, open ``<location of unzipped CodeChat files>/index.rst``. This file determines the hierarchical `document structure <http://sphinx-doc.org/markup/toctree.html>`_. For example, the following markup includes headings from ``README.rst`` into ``index.rst``::

   .. toctree::
      :maxdepth: 2

      README

One important note: when refering to files in subdirectories, a forward slash **MUST** be used, even on Windows. That is, use ``CodeChat/filename``, not ``CodeChat\filename``. Sphinx supports many other `markup constructs <http://sphinx-doc.org/markup/index.html>`_ as well.

Creating a new project
^^^^^^^^^^^^^^^^^^^^^^
To create a new Sphinx project, first create an empty directory to hold your project's files. In ``Settings | Settings | Sphinx``, select this directory as the project directory then click OK. A dialog box will pop up, asking if you'd like some default files copied. Click yes. Open the generated ``index.rst`` file. To add a file to your project, use ``File | New`` in Enki to create a new file, then save it as ``README.rst``. Generate some content in README.rst, including at least one heading, but notice that it isn't being rendered. To fix this, include it in your Sphinx project: in ``index.rst``, add it to your ``toctree`` directive::

   .. toctree::
      :maxdepth: 2

      README

When you switch back to ``README.rst``, it will now be rendered and included in your project.

.. [#] http://sphinx-doc.org/index.html

Basic CodeChat
--------------
Based on your familiarity with reST, we'll now explore embedding reST in the comments of a program. First, enable CodeChat in Enki's ``Settings | Settings | Literate Programming`` dialog by checking the "Enable CodeChat" checkbox. In ``Settings | Settings | Sphinx``, uncheck "Enable Sphinx" checkbox. Now, open ``<location of unzipped CodeChat files>/setup.py``. Notice that reST constructs, when correctly embedded in comments, render properly. Specifically, to be rendered using reST, a comment must:

#. Be a single-line comment; in C, multi-line capable ``/*`` and ``*/`` comments cannot be used.
#. Be the only non-whitespace characters on the line -- code cannot preceed the comment.
#. Have at least one space following the comment character(s) -- tabs don't work.

For example, in *C* or *C++* [#]_:

+-----------------------------------------------------------+-----------------------------------------------------------+
+ Source code                                               + CodeChat results                                          +
+===========================================================+===========================================================+
| .. code:: c                                               | ReST_ works *here*.                                       |
|                                                           |                                                           |
|    // ReST_ works *here*.                                 | .. code:: c                                               |
|    //But not here -- a space must follow the comment.     |                                                           |
|    /* Not here either. Only single-line comments work. */ |    //But not here -- a space must follow the comment.     |
|    a = 1; // Not here either. Comments must be on a       |    /* Not here either. Only single-line comments work. */ |
|    b = 2; // separate line, not following code.           |    a = 1; // Not here either. Comments must be on a       |
|                                                           |    b = 2; // separate line, not following code.           |
+-----------------------------------------------------------+-----------------------------------------------------------+

.. [#] Currently, only single-line comments in C/C++, Python, reST, assembly (.s), BASH scripts, PHP, MATLAB scripts, DOS batch (.bat) files, .ini, and .iss files are supported.

Now, open one of your source files. Modify your comments to add reST markup; add in titles, hyperlinks, and other useful markup.

While basic CodeChat usage shown here provides a quick way to begin experimenting with literate programming, it's limited in several ways. First, because it uses basic reST, CodeChat lacks the ability to create a web of documentation over multiple source files in a project. Second, the web page produced by CodeChat must be manually saved to disk for others to view, an inefficient process when providing documentation to others. Finally, the results are rather ugly. We therefore turn to Sphinx to remedy all these problems.

Basic Sphinx with CodeChat
--------------------------
Now, combining Sphinx with CodeChat enables the use of the literate programming paradigm applied to all source and accompanying documentation in a project. To see this in action, in ``Settings | Settings | Sphinx`` enable Sphinx; make sure the project directory is ``<location of unzipped CodeChat files>``. Now, open or switch to ``<location of unzipped CodeChat files>/setup.py``. Note that the source code is rendered to HTML for this file and for all source and documetnation files in the CodeChat project.

Now, create a new Sphinx with CodeChat project. First, choose a directory in which source files you'd like to document reside. In ``Settings | Settings | Sphinx``, select this direectory. After pressing OK, Enki will ask if you'd like to add the necessary template files; click OK. These files are different than the Sphinx-only template files from earlier, since both Sphinx and CodeChat are enabled. Now, transform your program into a document by adding titles, hyperlinks, etc. Explore the ``conf.py`` file, added as a template, to customize the output for your needs.

Reference
=========
* For basic reST syntax, see the `reST primer`_.
* For additional Sphinx-specific commands, refer to `markup constructs`_.
* For examples of literate programming in use, see below.

Style guide
-----------
In using CodeChat with Sphinx, I've developed a set of guidelines to make my code more consistent and readable:

* Carefully organize your code using sections. Based on Sphinx recommendations for `sections <http://sphinx-doc.org/rest.html#sections>`_, use:

  * In a toc-containing document use # with overline, for parts.
  * In each source file, use a single * with overline near the top of the file, giving the name of the file and a very brief description.
  * In a source file, use multiple =, for sections. Then, repeat for finer-grained items, as shown below.
  * Use - for subsections.
  * Use ^ for subsubsections.
  * Use " for subsubsubsections.

* Rather than leaving blank lines between code and a section, place empty comments. This makes the resulting HTML look better by suppressing an unnecessary newline. Specifically:

   +-----------------+-----------------+
   | Do              | Do not          |
   +=================+=================+
   | .. code::       | .. code::       |
   |                 |                 |
   |    void foo() { |    void foo() { |
   |    }            |    }            |
   |    //           |                 |
   |    // Section   |    // Section   |
   |    // =======   |    // =======   |
   +-----------------+-----------------+

* Headings must be placed on the far left of a file, even if it doesn't following the indentation of the source.

   +-----------------+---------------------+
   | Do              | Do not              |
   +===============+=+=====================+
   | .. code::       | .. code::           |
   |                 |                     |
   |    void foo() { |    void foo() {     |
   |    // Variables |        // Variables |
   |    // --------- |        // --------- |
   |        int i;   |        int i;       |
   |    }            |    }                |
   +-----------------+---------------------+

* Document functions, classes, parameters, etc. on the preeceding line.

  .. code::

     // Compute the number of bananas needed to provide a balanced diet.
     //
     // Return value: Amount of bananas, in pounds, needed.
     float banans_for_balanced_diet(
       // Amount of apples available, in pounds.
       float f_apples,
       // Amount of oranges available, in pounds.
       float f_orangs) {

         // Per `myPlate <http://www.choosemyplate.gov/food-groups/fruits-amount.pdf>`_,
         // the following calculations determine the needed mass of bananas.
         /// ...Code omitted...
      }

* Insert a per-source file table of contents (such as the one at the beginning of this file) to provide a quick overview of the file's structure.

* Avoid long lines; wrap your lines at 80 characters. Many editors aren't configured to wrap lines nicely, or can't do it well. They certainly won't wrap bulleted lists, indentation, etc. well. Make sure your code is readable in a plain text editor or IDE, not only when viewed using CodeChat. For example:

  * This will look a lot better and read more easily in most text editors when
    it is wrapped nicely.

* `Avoid tabs <http://tarantsov.com/hackers-coding-style-guide/why-tabs-should-be-avoided.html>`_. They make the resulting HTML less predictable. A tab after the inital comment character(s) won't be recognized as a reST-formatted comment.

* Use in-line `hyperlinks <http://sphinx-doc.org/rest.html#external-links>`_ (as in the document), rather than separating the links and its definition. Include hyperlinks to essential information you find while searching the web: that magic post from stackoverflow that solved (or promised to and didn't) your problem. Link to a reference manual when calling from a documented API. Link to other parts of your code that cooperate with the lines you're documenting.

* When commenting code out, use ``///`` (C, C++ -- although ``#if 0`` / ``#endif`` is better), ``##`` in Python, etc. Use similar structure to get a monospaced font when necessary. For example:

  .. code::

     # Don't do this now, still debugging.
     ##os.exit(0)

     ##        Max  Prefix   Hit ratio
     dump_objs(23,  'test_', 3.05)

* Use directives, such as `note <http://docutils.sourceforge.net/docs/ref/rst/directives.html#note>`_, to place highly visible reminders in your code.

  .. note::

     Need to work on this..

* Create diagrams, such as state diagrams, flow charts, etc. by `embedding Graphviz statements <http://sphinx-doc.org/ext/graphviz.html>`_ in your source code. It's painful to get started, but changing them as the code changes is a snap.

* Embed `figures <http://sphinx-doc.org/rest.html#images>`_ to better explain your program. For example, use external drawing programs to produce diagrams. Take a screenshot of a GUI or some graphical result from your code. Scan and mark up a datasheet, showing what choices you made in your code. Take a picture of your code in use -- GPS nagivation on a smart phone, etc.

* Avoid the use of `Sphinx domains <http://sphinx-doc.org/domains.html>`_. They're helpful when writing a separate document which describes code; literate programming intermingles code and documentation to produce an executable document, making it much easier to keep the content updated and relevant.

Examples
--------
Some examples of literate programming using CodeChat:

* `CodeChat itself <https://pythonhosted.org/CodeChat/>`_:

  * Use of tables to help design a `simple parser <https://pythonhosted.org/CodeChat/CodeChat/CodeToRest.py.html#preserving-empty-lines-of-code>`_.
  * Use of GraphViz to illustrate a `simple state machine <https://pythonhosted.org/CodeChat/CodeChat/CodeToRest.py.html#summary-and-implementation>`_.
  * Use of hyperlinks to provide reference information for all `Sphinx configuration values <https://pythonhosted.org/CodeChat/conf.py.html>`_.
  * Use of fonts to show what ``setup.py`` `commands to run <https://pythonhosted.org/CodeChat/setup.py.html>`_

* CodeChat is used for code examples in a course on `microprocessors <http://www.ece.msstate.edu/courses/ece3724/main_pic24/docs/sphinx/textbook_examples.html>`_.

Contributing
============
This is a fairly basic implementation; much improvement is needed! Please use the `issue tracker <http://bitbucket.org/bjones/documentation/issues?status=new&status=open>`_ to report bugs or request features; even better, or contribute to the code at the CodeChat_ homepage!
