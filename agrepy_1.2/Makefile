VERSION=1.2

PYTHON_VERSION=2.3

# Edit this to point to the directory tree in which Python is found
PYTHONROOT=/sw
# PYTHONROOT=/usr/local

# Linux
CC = gcc


# When testing
# Uncomment one of these when creating C only version for testing (see also output below)
# CFLAGS = -g -Wall -Wshaddow  -DDEBUG -DDEBUGDEBUG   #  for agrepy_test
# CFLAGS = -g #  for agrepy_test (free standing C application)
OPTFLAGS =  -O3 -funroll-loops

# The following flag is relevant to Linux but is not not recognized
# by MacOS X  posix compiler so comment it out
# LDFLAGS = -shared

# Some compilers (not Mac) insist you add -fpic when compiling to get .so
# LDFLAGS = -shared -fPIC

# For Mac OSX
# You will need to make the final argument refer to where the binary lives
LDFLAGS = -bundle -bundle_loader $(PYTHONROOT)/bin/python$(PYTHON_VERSION)

CFLAGS= -DPYTHON $(FPIC) $(OPTFLAGS)

INCLUDES = -I$(PYTHONROOT)/include/python$(PYTHON_VERSION)

ALLOBJS = sagrepy.o lagrepy.o agrepy.o agrepy_wrap.o
TESTOBJS = sagrepy.o lagrepy.o agrepy.o

# Uncomment output : agrepy_test  when building C only version for testing
output :  _agrepy.so
# output : agrepy_test

# This is a C-only implementation for testing purposes
agrepy_test:  $(TESTOBJS)
	$(CC) $(CFLAGS) -DSTANDALONE -o agrepy_test $(TESTOBJS)

_agrepy.so : $(ALLOBJS)
	$(CC) $(LDFLAGS)  $(ALLOBJS) -o $@

%.o: %.c
	$(CC) $(CFLAGS) -c $< $(INCLUDES)

agrepy_wrap.c : agrepy.i
	swig -python agrepy.i


$(ALLOBJS): agrepy.h


clean: 
	rm -f $(ALLOBJS) agrepy_wrap.doc

new:
	rm -f $(ALLOBJS)
	make 

tarfile:
	mkdir agrepy_${VERSION}
	cp `cat FILES` agrepy_${VERSION}
	cp FILES agrepy_${VERSION}
	tar cvf agrepy_${VERSION}.tar agrepy_${VERSION}
	gzip agrepy_${VERSION}.tar
	/bin/rm -r agrepy_${VERSION}
