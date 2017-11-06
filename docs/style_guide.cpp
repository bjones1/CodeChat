// .. Copyright (C) 2012-2017 Bryan A. Jones.
//
//  This file is part of CodeChat.
//
//  CodeChat is free software: you can redistribute it and/or modify it under
//  the terms of the GNU General Public License as published by the Free
//  Software Foundation, either version 3 of the License, or (at your option)
//  any later version.
//
//  CodeChat is distributed in the hope that it will be useful, but WITHOUT ANY
//  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
//  FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
//  details.
//
//  You should have received a copy of the GNU General Public License along
//  with CodeChat.  If not, see <http://www.gnu.org/licenses/>.
//
//
// .. Tell Sphinx to use the C++ syntax highligher for this file, instead of the
//  default Python highligher.
//
// .. highlight:: c++
//
// ****************************************************
// style_guide.cpp - Style recommendations for CodeChat
// ****************************************************
// .. note::
//
//  This "source file" does not contain any useful, executable code. Instead,
//  it exemplifies literate programming style.
//
// Syntax
// ======
// Before covering style, the following shows the syntax used to embed reST in
// comments. The rules used to determine if a comment will be interpreted as
// reST are:
//
// #.   A comment must be placed on a line containing only comments or whitespace,
//      but no code, preprocessor directives, etc.
// #.   One space must follow the opening comment delimier.
//
// The following provide examples of the source code and its interpretation. The
// following source code...
//
// .. code-block:: c
//  :linenos:
//
//  // A line containing only a comment in interpred as reST.
//      // Indented lines will be properly indented in the output, as well.
//      /* Block comments may also be used.
//         They may span multiple lines. */
//          /* Block comment indents are
//           * preserved, as well.
//           */
//      i = 0; // Comments with code are not
//      j = 1; /* interpreted as reST. */
//
// ...becomes...
//
// A line containing only a comment in interpred as reST.
    // Indented lines will be properly indented in the output, as well.
    /* Block comments may also be used.
       They may span multiple lines. */
        /* Block comment indents are
         * preserved, as well.
         */
    i = 0; // Comments with code are not
    j = 1; /* interpreted as reST. */
//
// Guidelines
// ==========
// In using CodeChat with Sphinx, I've developed a set of guidelines to make my
// code more consistent and readable. These are my recommendations. Refer to the
// examples in :doc:`../README` to see these principles applied to actual source
// code.
//
// *    Carefully organize your code using sections. Based on Sphinx
//      recommendations for `sections <http://sphinx-doc.org/rest.html#sections>`_,
//      use:
//
//      *   In a TOC-containing document, use ``@`` with overline for large parts.
//          See, for example, :doc:`../index`.
//      *   In a TOC-containing document use ``#`` with overline, for parts. Again,
//          see :doc:`../index`
//      *   In each source file, use a single ``*`` with overline near the top of the
//          file, giving the name of the file and a very brief description. See the
//          title above as an example.
//      *   In a source file, use multiple ``=`` for sections. Then, repeat for
//          finer-grained items, as shown below. The source files in this package,
//          such as :doc:`../setup.py`, demonstrate this.
//      *   Use ``-`` for subsections.
//      *   Use ``^`` for subsubsections.
//      *   Use ``"`` for subsubsubsections.
//
// *    Rather than leaving blank lines between code and a section, place empty
//      comments. This makes the resulting HTML look better by suppressing an
//      unnecessary newline. For example, correct use is:
    void foo() {
    }
//
// Title
// -----
//      Note that the comment character before the section title suppresses a
//      newline.
//
//      Incorrect:
        void foo() {
        }

// Title
// -----
//      Note the unnecesary newline before the section title above.
//
// *    Headings may be indented, but this causes problems in the resulting HTML by
//      indenting too much. **Avoid this.**
    void foo(int i_sum) {
        if (i_sum) {
            // Indented heading -- **bad**
            // ---------------------------
            // This comment isn't indented as it should be, one bad result of
            // indenting a heading.
            assert(i_sum > 1);
            // Another indented heading -- **bad**
            // ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
            // The indentation on this heading is wrong, too, another bad
            // result. In fact, *everything* will be indented until the next
            // heading. For example, the following code and comments will be
            // extremely overindented.
            bar(i_sum);
            // Overindented text.
//
// An unindented heading -- correct
// ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        // Now, text and code will be indented correctly.
//
// *    Document functions, classes, parameters, etc. on the preeceding line. For
//      example:
//
//   Provide a series of utilities to assist in eating a balanced diet.
    class DietBalancer {
        // Compute the number of bananas needed to provide a balanced diet.
        //
        // Return value: Amount of bananas, in pounds, needed.
        int bananas_for_balanced_diet(
          // Amount of apples available, in pounds.
          apples,
          // Amount of oranges available, in pounds.
          orangs) {

            // Per `myPlate <http://www.choosemyplate.gov/food-groups/fruits-amount.pdf>`_,
            // the following calculations determine the needed mass of bananas.
            /// ...Code omitted...
//
// *    Insert a per-source file table of contents (such as the one at the
//      beginning of :doc:`../README`) to provide a quick overview of the file's
//      structure.
//
// *    Avoid long lines; wrap your lines at 80 characters. Many editors aren't
//      configured to wrap lines nicely, or can't do it well. They certainly won't
//      wrap bulleted lists, indentation, etc. well. Make sure your code is
//      readable in a plain text editor or IDE, not only when viewed using
//      CodeChat.
//
// *    `Avoid tabs
//      <http://tarantsov.com/hackers-coding-style-guide/why-tabs-should-be-avoided.html>`_.
//      They make the resulting HTML less predictable. A tab after the inital
//      comment character(s) won't be recognized as a reST-formatted comment.
//
// *    Select tab stops and stick with them. Don't indent based on the size of
//      the preceeding reST element -- this makes code difficult to edit. For
//      example, note how this list is constructed: not as ``* A bullet
//      here...``, but ``*    A bullet here`` to align with tab stops. (Per the
//      preceeding point, no tabs are used, just tab stops; in my case, all
//      indents are aligned to 4 space boundaries.)
//
// *    Use in-line `hyperlinks <http://sphinx-doc.org/rest.html#external-links>`_
//      (as in this document), rather than separating the link and its definition.
//      Include hyperlinks to essential information you find while searching the
//      web: that magic post from stackoverflow that solved (or promised to and
//      didn't) your problem. Link to a reference manual when calling from a
//      documented API. Link to other parts of your code that cooperate with the
//      lines you're documenting.
//
// *    When commenting code out, use ``///`` (C, C++ -- although ``#if 0`` /
//      ``#endif`` is better), ``##`` in Python, etc. For example:
    // Don't do this now, still debugging.
    /// exit(0);
//
//   Use a similar structure to get a monospaced font when necessary. For example:
    ///       Max  Prefix   Hit ratio
    dump_objs(23,  "test_", 3.05);
//
// *    Use directives, such as `note
//      <http://docutils.sourceforge.net/docs/ref/rst/directives.html#note>`_,
//      to place highly visible reminders in your code.
//
//      .. note::
//
//          Need to work on this.
//
// *    Use `reST comments <http://sphinx-doc.org/rest.html#comments>`_ to hide
//      text in the output. At the top of the this file, the file's license is
//      present in the source, but not included in the output through the use of
//      reST comments.
//
// *    Create diagrams, such as state diagrams, flow charts, etc. by `embedding
//      Graphviz statements <http://sphinx-doc.org/ext/graphviz.html>`_ in your
//      source code. It's painful to get started, but changing them as the code
//      changes is a snap.
//
// *    Embed `figures <http://sphinx-doc.org/rest.html#images>`_ to better explain
//      your program. For example, use external drawing programs to produce
//      diagrams. Take a screenshot of a GUI or some graphical result from your
//      code. Scan and mark up a datasheet, showing what choices you made in your
//      code. Take a picture of your code in use -- GPS nagivation on a smart phone,
//      etc.
//
// *    Avoid the use of `Sphinx domains <http://sphinx-doc.org/domains.html>`_.
//      They're helpful when writing a separate document which describes code;
//      literate programming intermingles code and documentation to produce an
//      executable document, making it much easier to keep the content updated and
//      relevant.
