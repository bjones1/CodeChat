# Hidden imports
hiddenimports = ['sphinx.cmdline', 'sphinx.domains.cpp', 'sphinx.writers.html', 'sphinx.util.smartypants', 'sphinx.util.docfields', 'sphinx.addnodes', 'sphinx.writers.manpage', 'sphinx.pycode.pgen2.parse', 'sphinx.pycode.pgen2.grammar', 'sphinx.errors', 'sphinx.domains.c', 'sphinx.util.png', 'sphinx.util.tags', 'sphinx.directives', 'sphinx.pycode.nodes', 'sphinx.jinja2glue', 'sphinx.theming', 'sphinx.pycode.pgen2.token', 'sphinx.highlighting', 'sphinx.writers.latex', 'sphinx.writers', 'sphinx.domains.std', 'sphinx.pycode', 'sphinx.directives.other', 'sphinx.util.osutil', 'sphinx.util', 'sphinx.domains.javascript', 'sphinx.directives.code', 'sphinx.builders.html', 'sphinx.environment', 'sphinx.util.compat', 'sphinx.ext.autodoc', 'sphinx.util.jsdump', 'sphinx.ext.mathbase', 'sphinx.util.matching', 'sphinx.pycode.pgen2.pgen', 'sphinx.builders', 'sphinx.util.stemmer', 'sphinx.util.jsonimpl', 'sphinx.roles', 'sphinx.util.nodes', 'sphinx.pycode.pgen2.driver', 'sphinx.pycode.pgen2.tokenize', 'sphinx.pycode.pgen2', 'sphinx.util.texescape', 'sphinx.util.inspect', 'sphinx.util.docstrings', 'sphinx.locale', 'sphinx.writers.text', 'sphinx.util.pycompat', 'sphinx.application', 'sphinx.search', 'sphinx.ext.pngmath', 'sphinx.ext', 'sphinx.ext.oldcmarkup', 'sphinx.domains.rst', 'sphinx.domains', 'sphinx.pycode.pgen2.literals', 'sphinx.domains.python', 'sphinx.util.console', 'sphinx.config', 'jinja2.ext']

# Data files
import os
import sys

def sphinx_data_files():
  mod_str = "sphinx";
  mod = __import__(mod_str);
  
  if hasattr(mod,'__file__'):
    mod_dir = os.path.dirname(mod.__file__);
  else:
    return;

  data_files = [];
  for dir, dirnames, files in os.walk(mod_dir):
    for f in files:
      fpath = os.path.join(dir,f);
      if '.py' not in f and not os.path.isdir(fpath):
        data_files.append(fpath);

  datas = [];
  for file in data_files:
    orig_file = file;

    file = file.replace(mod_dir,"");
    file = file.replace(os.path.split(file)[1],"");

    if file[0] == os.sep:
      file = file[1:];
    
    file = mod_str + os.sep + file; 

    datas.append((orig_file,file));

  return datas;

datas = sphinx_data_files();
