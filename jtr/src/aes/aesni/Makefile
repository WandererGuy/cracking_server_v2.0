
CC = gcc
ASM_DIR = asm/x$(AESNI_ARCH)
IAES = $(ASM_DIR)/iaesx$(AESNI_ARCH).s
RDTSC = $(ASM_DIR)/do_rdtsc.s
YASM = 

iaesx.o: $(IAES)
	$(YASM) -D__cygwin__ -f win64 $(IAES) -o $@

rdtsc.o: $(RDTSC)
	$(YASM) -D__cygwin__ -f win64 $(RDTSC) -o $@

aesni.o: iaes_asm_interface.h  iaesni.h  intel_aes.c
	$(CC) $(CFLAGS) -Wall -Wno-stringop-truncation -Wno-format-overflow -Wno-format-truncation -fno-omit-frame-pointer -Wno-deprecated-declarations -Wunused-but-set-variable -Wdate-time -D_GNU_SOURCE -D__CYGWIN64__ -D__CYGWIN32__ -m64 -c intel_aes.c -o $@

all: iaesx.o rdtsc.o aesni.o

default: all

clean:

distclean: clean
	$(RM) Makefile
