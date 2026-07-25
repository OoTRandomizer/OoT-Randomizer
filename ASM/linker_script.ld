SECTIONS
{
    /* Allocatable and important sections */
    .text   : { *(.text*);   }
    .rodata : { *(.rodata*); }

    /*
     * Put the NOLOAD sections (bss, sbss, etc) into data to
     * force them to be in the ROM
     */
    .data   : { *(.data*);   *(.bss*);  *(COMMON);  }
    .sdata  : { *(.sdata*); *(.sbss*); *(.scommon); }

    /* Not allocatable sections that may be useful */
    .reginfo          : { *(.reginfo); }
    .pdr              : { *(.pdr); }
    .gnu.attributes   : { KEEP (*(.gnu.attributes)); }
    .mdebug           : { *(.mdebug); }
    .mdebug.abi32     : { *(.mdebug.abi32); }

    /* Useless allocatable sections */
    /DISCARD/ : {
        *(.MIPS.abiflags)
        *(.MIPS.options)
        *(.note.gnu.build-id)
        *(.got)
        *(.interp)
        *(.eh_frame)
        *(.reginfo)
    }
}
z64_ActorFind = 0x80025B0C;
KaleidoManager_GetRamAddr =  0x80099DBC;
DmaMgr_RequestSync = 0x80000df0;
