#!/usr/bin/env python

'''
This is a simple test program for the dynamically loaded implementation of agrepy
created from the C files agrepy.c, sagrepy.c and lagrepy.c via SWIG and agrepy.i
'''

import sys, string
import  agrepy

def testagrepy(query_string, text_string_list, NErrs, Gotoends, params_struct):
  for i in text_string_list:
    i = i[:-1]  # remove trailing \n
    print "Input line",i
    sys.stdout.flush()
    l = agrepy.agrepy(query_string, len(query_string), i, len(i), Gotoends, params_struct)
    print l
    del l

def init() :
  NErrs = 1
  Gotoends = 0
  query_string = None
  if len(sys.argv) < 2 :
    sys.stderr.write("Usage: %s [-N] [-e] [-s <search string>] <text file>\n" % sys.argv[0])
    sys.stderr.write("\tIf the search string is not on the command line, the user will be prompted for it\n")
    sys.stderr.write("\tIf -N is not used (N the max number of errors) the default value is: %d\n" % NErrs)
    sys.stderr.write("\tIf -e used matches extend to the limits of the pattern, rather than the first and last real matches\n");
    sys.exit(1)

  argix = 1
  while sys.argv[argix][0] == '-' :
    if sys.argv[argix][1] == 's' :
      query_string = sys.argv[argix+1]
      argix = argix + 2
    elif sys.argv[argix][1] == 'e' :
      Gotoends = 1
      argix = argix + 1
    elif sys.argv[argix][1] >= '0' and sys.argv[argix][1] <= '9' :
      try:
	NErrs = string.atoi(sys.argv[argix][1:])
	# if NErrs < 1 or NErrs > 8 :
	  # raise ValueError
	argix = argix + 1
      except ValueError:
	sys.stderr.write("%s is not an integer following the '-', or is not in the range 1..8\n" % sys.argv[argix][1:])
	sys.exit(1)
    else :
      sys.stderr.write("Unknown option %s\n" % sys.argv[argix])
      sys.exit(1)
  try:
    infile = open(sys.argv[argix], 'r')
  except:
    raise "%s: Cannot open text file %s\n" % (sys.argv[0], sys.argv[argix])

  return((infile.readlines(), NErrs, Gotoends, query_string))

if __name__ == "__main__" :
  (text_lines, NErrs, Gotoends, query_string) = init()
  if query_string != None :
    params_struct = agrepy.compile(query_string, len(query_string), NErrs)
    testagrepy(query_string, text_lines, NErrs, Gotoends, params_struct)
  else :
    while 1:
      try:
	query_string = raw_input("Enter query string:")
      except EOFError:
        break
      params_struct = agrepy.compile(query_string, len(query_string), NErrs)
      testagrepy(query_string, text_lines, NErrs, Gotoends, params_struct)
