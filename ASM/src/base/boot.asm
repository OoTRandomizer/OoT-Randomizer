; Add dmatable entries for new code
; Remove the unused files at the bottom the DMA Table
;   - this isn't strictly necessary, but adds flexibility for the future
.orga 0xD1B0
.area 0x100, 0
    .word 0x03480000, 0x03480000 + PAYLOAD_END - PAYLOAD_START, 0x03480000, 0
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
;   addiu   t7, r0, 0x00F0
.orga 0xB17BB4 ; In memory: 0x800A1C54
.area 0x24, 0
    sw      ra, 0x001C (sp)
    sw      a0, 0x0140 (sp)

    ; Load first code file from ROM
    lui     a0, 0x8040
    li      a2, PAYLOAD_END - PAYLOAD_START
    jal     0x80000DF0
    lui     a1, 0x0348

    jal     init
    nop
.endarea
