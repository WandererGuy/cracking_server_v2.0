
CC = gcc
CXX = @CXX@
AS = gcc
LD = gcc
CPP = gcc
CFLAGS = -g -O2 -DARCH_LITTLE_ENDIAN=1 -DPREFER_FLOCK -Wall -Wno-stringop-truncation -Wno-format-overflow -Wno-format-truncation -fno-omit-frame-pointer -Wno-deprecated-declarations -Wunused-but-set-variable -Wdate-time -D_GNU_SOURCE -D__CYGWIN64__ -D__CYGWIN32__ 
ASFLAGS =  -DARCH_LITTLE_ENDIAN=1 -c  -D__CYGWIN64__ -D__CYGWIN32__
LDFLAGS =  -L/usr/local/lib  -lssl -lcrypto
YASM = 
AR = /usr/bin/ar
FIND = /usr/bin/find
RM = /bin/rm -f
GCCV44 := $(shell expr `$(CC) -dumpversion | cut -d '.' -f 1` \>= 4)
USE_AESNI = cygwin

AESIN = aes.o openssl/ossl_aes.o
SUBDIRS = openssl
ifeq "$(GCCV44)" "1"
	ifneq "$(YASM)" ""
		ifdef USE_AESNI
			ifdef AESNI_ARCH
				AESIN += aesni/*.o
				SUBDIRS += aesni
				AESNI_DEC = -DAESNI_IN_USE
			endif
		endif
	endif
endif

aes.o: aes.c ../aes.h aes_func.h
	$(CC) $(CFLAGS) $(AESNI_DEC) -c aes.c -o aes.o

.PHONY: subdirs $(SUBDIRS)

subdirs: $(SUBDIRS)

$(SUBDIRS):
	$(MAKE) -C $@ all

aes.a: $(SUBDIRS) aes.o
	$(AR) -rs $@ $(AESIN)

default: aes.a
all: aes.a

clean:
	$(FIND) . -name \*.a -exec $(RM) {} \;
	$(FIND) . -name \*.o -exec $(RM) {} \;

distclean: clean
	$(RM) Makefile
	$(RM) aesni/Makefile
	$(RM) openssl/Makefile
