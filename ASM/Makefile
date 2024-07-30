CC = mips64-gcc
LD = mips64-ld
OBJDUMP = mips64-objdump
OBJCOPY = mips64-objcopy

CFLAGS = -O1 -G0 -fno-reorder-blocks -march=vr4300 -mtune=vr4300 -mabi=32 -mno-gpopt -mdivide-breaks \
	-mexplicit-relocs
CPPFLAGS = -DF3DEX_GBI_2

OUTDIR := build
OBJDIR := build/bin
SRCDIR := c
vpath %.c c
vpath %.h c
RESOURCEDIR := resources

UC = $(shell echo '$1' | tr '[:lower:]' '[:upper:]')

OBJECTS = $(patsubst $(SRCDIR)/%.c,$(OBJDIR)/%.o,$(sort $(wildcard $(SRCDIR)/*.c)))
RESOURCES = $(patsubst $(RESOURCEDIR)/%.bin,$(OBJDIR)/%_bin.o,$(sort $(wildcard $(RESOURCEDIR)/*.bin)))

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

$(OBJDIR)/%_bin.o: $(RESOURCEDIR)/%.bin
	$(OBJCOPY) -I binary -O elf32-bigmips --rename-section .data=.rodata,alloc,load,readonly,data,contents $< $@
	$(OBJCOPY) --redefine-sym _binary_resources_$*_bin_start=$(call UC,$*)_RESOURCE $@
	$(OBJCOPY) --redefine-sym _binary_resources_$*_bin_end=$(call UC,$*)_RESOURCE_END $@
	$(OBJCOPY) --redefine-sym _binary_resources_$*_bin_size=$(call UC,$*)_RESOURCE_SIZE $@


$(RESOURCEDIR):
	mkdir -p $@

$(OBJECTS): | $(OBJDIR)

$(RESOURCES): | $(RESOURCEDIR)

bundle: $(RESOURCES) $(OBJECTS)
	$(LD) -T linker_script.ld -T ootSymbols.ld -o $(OUTDIR)/bundle.o -i -L. $(patsubst %.o,-l:%.o,$(OBJECTS) $(RESOURCES))

symbols: bundle
	$(OBJDUMP) -t $(OUTDIR)/bundle.o | tr -d '\015' > $(OUTDIR)/c_symbols.txt
ifdef RUN_OBJDUMP
		$(OBJDUMP) -d $(OUTDIR)/bundle.o | tr -d '\015' > $(OUTDIR)/bundle_d.txt
		$(OBJDUMP) -r $(OUTDIR)/bundle.o | tr -d '\015' > $(OUTDIR)/bundle_r.txt
endif

clean:
	rm -f $(OBJDIR)/*.o
