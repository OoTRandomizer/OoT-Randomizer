CC = mips64-gcc
LD = mips64-ld
OBJDUMP = mips64-objdump

CFLAGS = -O1 -G0 -fno-reorder-blocks -march=vr4300 -mtune=vr4300 -mabi=32 -mno-gpopt -mdivide-breaks \
	-mexplicit-relocs
CPPFLAGS = -DF3DEX_GBI_2

OUTDIR := build
OBJDIR := build/bin
SRCDIR := c
vpath %.c c
vpath %.h c

OBJECTS = $(patsubst $(SRCDIR)/%.c,$(OBJDIR)/%.o,$(sort $(wildcard $(SRCDIR)/*.c)))

.PHONY: all clean bundle symbols

all: clean bundle symbols

$(OBJDIR)/%.o: %.c 
	$(CC) -o $@ -c $< $(CFLAGS) $(CPPFLAGS)
ifdef RUN_OBJDUMP
		$(OBJDUMP) -d $@ | tr -d '\015' > $@_d.txt
		$(OBJDUMP) -r $@ | tr -d '\015' > $@_r.txt
endif

$(OBJDIR): 
	mkdir -p $@

$(OBJECTS): | $(OBJDIR)

bundle: $(OBJECTS)
	$(LD) -T linker_script.ld -o $(OUTDIR)/bundle.o -i -L. $(patsubst %.o,-l:%.o,$(OBJECTS))

symbols: bundle
	$(OBJDUMP) -t $(OUTDIR)/bundle.o | tr -d '\015' > $(OUTDIR)/c_symbols.txt
ifdef RUN_OBJDUMP
		$(OBJDUMP) -d $(OUTDIR)/bundle.o | tr -d '\015' > $(OUTDIR)/bundle_d.txt
		$(OBJDUMP) -r $(OUTDIR)/bundle.o | tr -d '\015' > $(OUTDIR)/bundle_r.txt
endif

clean:
	rm -f $(OBJDIR)/*.o
