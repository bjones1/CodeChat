// <!--- Copyright (C) 2012-2020 Bryan A. Jones.
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
// -->
//
// # style_guide.md.cpp - Style recommendations for CodeChat using Markdown
//
// CodeChat's Sphinx extension also supports Markdown.
//
//  > Note: this "source file" does not contain any useful, executable code. Instead, it exemplifies literate programming style.
//
// ## Use
// Any file with an extension of `.<markdown extension>.<source file extension>` will be processed as Markdown; for example, see this file's name. The ``<markdown extension>`` is defined as any key in Sphinx's [source_suffix](https://www.sphinx-doc.org/en/master/usage/configuration.html#confval-source_suffix) build configuration file whose value is `"markdown"`. See the [Sphinx manual on Markdown](https://www.sphinx-doc.org/en/master/usage/markdown.html) for more information. This feature requires ``recommonmark`` to be installed, as discussed in the previous link.
//
// ## Syntax
// The same [syntax](CodeChat_syntax) rules apply to Markdown; see [here](https://commonmark.org/help/) for basic Markdown syntax.
//
// ## Advice
// At the present, the author doesn't use Markdown with CodeChat; however, the information at [style_guide.cpp](style_guide.cpp) mostly applies. Instead, this file simply serves as an example of using Markdown with CodeChat.