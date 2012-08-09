import os
import sys

def get_mods(mod_str):
  mod = __import__(mod_str);
  
  mods = set();
  mods.add(mod_str);

  mod_dir = os.path.dirname(mod.__file__);
  for dirpath, dirnames, filenames in os.walk(mod_dir):
    mod_path = dirpath.replace(mod_dir,"").replace(os.sep,".");
   
    if mod_path == "":
      mod_path = mod_str;
    else:
      mod_path = mod_path[1:];
      mod_path = mod_str + "." + mod_path;

    if '__init__.py' in os.listdir(dirpath):
      mods.add(mod_path);

    for file in filenames:
      if file[-3:] == ".py" and '__init__' not in file:
        mods.add( mod_path + "." + file.replace(".py","") );

  return mods;

hiddenimports = list(get_mods('docutils'));

def docutils_data_files():
  mod_str = "docutils";
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

datas = docutils_data_files();
