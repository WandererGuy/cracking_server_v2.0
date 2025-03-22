
CC = gcc
CXX = @CXX@
AS = gcc
LD = gcc
CPP = gcc
CFLAGS = -g -O2 -DARCH_LITTLE_ENDIAN=1 -DPREFER_FLOCK -Wall -Wno-stringop-truncation -Wno-format-overflow -Wno-format-truncation -fno-omit-frame-pointer -Wno-deprecated-declarations -Wunused-but-set-variable -Wdate-time -D_GNU_SOURCE -D__CYGWIN64__ -D__CYGWIN32__ 
ASFLAGS =  -DARCH_LITTLE_ENDIAN=1 -c  -D__CYGWIN64__ -D__CYGWIN32__
LDFLAGS =  -L/usr/local/lib  -lssl -lcrypto

ossl_aes.o: ossl_aes.c ossl_aes.h
	$(CC) $(CFLAGS) -c ossl_aes.c -o $@

default: ossl_aes.o
all: ossl_aes.o

clean:

distclean: clean
	$(RM) Makefile
