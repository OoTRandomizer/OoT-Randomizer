; Hacks in BgMoriBigst (Forest temple falling platform/stalfos fight)
.headersize(0x80927020 - 0xCC4790)

; Increase the size of the actor instance so we can store explicit references to the spawned enemy
.org 0x8092782c
    .word   0x0000016C

; Hack the stalfos spawns for enemy drop shuffle to add a subflag
; Replaces the calls to Actor_SpawnAsChild in BgMoriBigst_SetupStalfosFight
.org 0x8092731c
    jal     BgMoriBigst_SpawnSingleStalfos
; and in BgMoriBigst_SetupStalfosPairFight
.org 0x809275c4
    jal     BgMoriBigst_SpawnStalfosPair1
.org 0x80927624
    jal     BgMoriBigst_SpawnStalfosPair2

; Hack BgMoriBigst_StalfosFight to check for children explicitly instead of using z rotation
; Replacing the function pointer to BgMoriBigst_StalfosFight (reloc 0x29C)
.org 0x809272bc
; Replaces:
;   lui         a1, 0x8092
;   addiu       a1, a1, 0x735c
    lui         a1, hi(BgMoriBigst_StalfosFight_new)
    addiu       a1, a1, lo(BgMoriBigst_StalfosFight_new)

; Hack BgMoriBigst_StalfosPairFight to check for children explicitly instead of using z rotation
; Replacing the function pointer to BgMoriBigst_StalfosPairFight (reloc 0x540)
.org 0x80927560
; Replaces:
;   lui         a1, 0x8092
;   addiu       a1, a1, 0x7660
    lui         a1, hi(BgMoriBigst_StalfosPairFight_new)
    addiu       a1, a1, lo(BgMoriBigst_StalfosPairFight_new)

; Patch relocs
; 0x29C
.org 0x809278c8
    nop
    nop
; 0x540
.org 0x80927908
    nop
    nop