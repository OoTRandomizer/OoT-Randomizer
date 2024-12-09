# Makefile for building vadpcm_enc and vadpcm_dec for either IRIX or natively.
# For an IRIX build, the env variable IRIX_ROOT should point to the root of an
# IRIX filesystem, and QEMU_IRIX should point to the qemu-irix binary.

NATIVE_CC := gcc
NATIVE_CFLAGS := -g -Wall -Wno-unused-result -Wno-uninitialized

default: native
all: native

native: vadpcm_enc_shared

clean:
	$(RM) *.o vadpcm_enc_native vadpcm_enc_shared

%.o: %.c
	$(IRIX_CC) -c $(IRIX_CFLAGS) $< -o $@

vadpcm_enc_shared: vadpcm_enc.c vpredictor.c quant.c util.c vencode.c
	$(NATIVE_CC) -shared $^ -o $@ -lm -fPIC

.PHONY: default all irix native clean
