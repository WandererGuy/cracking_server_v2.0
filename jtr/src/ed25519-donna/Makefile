
CC = gcc
CXX = @CXX@
AS = gcc
LD = gcc
CPP = gcc
CPPFLAGS =  -DCL_SILENCE_DEPRECATION
CFLAGS = -g -O2 -DARCH_LITTLE_ENDIAN=1 -DPREFER_FLOCK -Wall -Wno-stringop-truncation -Wno-format-overflow -Wno-format-truncation -fno-omit-frame-pointer -Wno-deprecated-declarations -Wunused-but-set-variable -Wdate-time -D_GNU_SOURCE -D__CYGWIN64__ -D__CYGWIN32__  -Wno-unused-function
ASFLAGS =  -DARCH_LITTLE_ENDIAN=1 -c  -D__CYGWIN64__ -D__CYGWIN32__
LDFLAGS =  -L/usr/local/lib  -lssl -lcrypto
YASM = 
AR = /usr/bin/ar
FIND = /usr/bin/find
RM = /bin/rm -f

IN = ed25519-donna.o

all: ed25519-donna.a
default: ed25519-donna.a

ed25519-donna.o: ed25519-donna.c
	$(CC) -DHAVE_CONFIG_H $(CFLAGS) $(CPPFLAGS) -c ed25519-donna.c -o ed25519-donna.o

.PHONY: subdirs $(SUBDIRS)

subdirs: $(SUBDIRS)

$(SUBDIRS):
	$(MAKE) -C $@ all

ed25519-donna.a: $(SUBDIRS) ed25519-donna.o
	$(AR) -rs $@ $(IN)

clean:
	$(FIND) . -name \*.a -exec $(RM) {} \;
	$(FIND) . -name \*.o -exec $(RM) {} \;

distclean: clean
	$(RM) Makefile
