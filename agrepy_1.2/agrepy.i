%module agrepy
%{
#include "agrepy.h"
%}

%typemap(python, out) int_pair_list * {
  int_pair_list *plist = $1;
  PyObject *retlist, *temp_tuple, *pyint;
  int i;

  if(plist == NULL)
    {
    Py_INCREF(Py_None);
    return Py_None;
    }

  retlist = PyList_New(plist -> npairs + 1);
  for(i=0; i<= plist -> npairs; i++)
    {
    temp_tuple =  PyTuple_New(2);
    PyTuple_SetItem(temp_tuple, 0, PyInt_FromLong(plist -> pairs[i].start));
    PyTuple_SetItem(temp_tuple, 1, PyInt_FromLong(plist -> pairs[i].end));
    PyList_SetItem(retlist, i, temp_tuple);
    }
  free(plist -> pairs);
  free(plist);
  return(retlist);
}
  


param_struct *compile(char* Pattern, int patlen, int NErrors);
int_pair_list *agrepy(char *pat, int patlen, char *text, int textlen, int gotoends, param_struct *parampt);
