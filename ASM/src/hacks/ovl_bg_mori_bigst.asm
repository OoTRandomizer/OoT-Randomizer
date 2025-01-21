; Hacks in BgMoriBigst (Forest temple falling platform/stalfos fight)
.headersize(0x80927020 - 0xCC4790)
; Hack the stalfos spawns for enemy drop shuffle to add a subflag
; Replaces the calls to Actor_SpawnAsChild in BgMoriBigst_SetupStalfosFight
.org 0x8092731c
    jal     BgMoriBigst_SpawnSingleStalfos
; and in BgMoriBigst_SetupStalfosPairFight
.org 0x809275c4
    jal     BgMoriBigst_SpawnStalfosPair1
.org 0x80927624
    jal     BgMoriBigst_SpawnStalfosPair2