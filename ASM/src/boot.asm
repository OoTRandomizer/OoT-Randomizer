; Update CRC
.org 0x10
    .word 0x0107B6D3, 0x14301B2F

; Add dmatable entries for new code
; Remove the unused files at the bottom the DMA Table
;   - this isn't strictly necessary, but adds flexibility for the future
.org 0xD1B0
    .word 0x03480000, 0x03490000, 0x03480000, 0, 0x03490000, 0x03500000, 0x03490000, 0 ;edit accept86
;Edit - Accept86, added File in DMATable 0x03490000-0x03500000 => this one does not get compressed via dmatable.dat (there was trouble with going out of the bounds of the actual ROM with my dmaload)

.area 0x0D0, 0  ; Edit Accept86 This Area was changed, because the compressor somehow didnt like the old version and there was a dmatable entry missing, that normally appears behind the upper file 
    ;.word 0x03480000, 0x03490000, 0x03480000, 0
.endarea 

; Load new code from ROM
; Replaces:
;   lui     v0, 0x8012
;   addiu   v0, v0, 0xD2A0
;   sw      ra, 0x001C (sp)
;   sw      a0, 0x0140 (sp)
;   addiu   t6, r0, 0x0140
;   lui     at, 0x8010
;   sw      t6, 0xE500 (at)
;   lui     at, 0x8010


.org 0xB17BB4 ; In memory: 0x800A1C54
    sw      ra, 0x001C (sp)
    sw      a0, 0x0140 (sp)

    ; Load first code file from ROM
    lui     a0, 0x8040
    lui     a1, 0x0348
    jal     0x80000DF0
    lui     a2, 0x0001

    jal     init
    nop
