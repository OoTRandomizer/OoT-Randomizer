; Bg_Haka_Tubo Hacks (Shadow Temple Spinning Pots)
.headersize(0x8099bec0 - 0xd30b50)

; Hack 3 spinning pot drops to drop overridden items

.org 0x8099c34c ; Hack when setting up the params to Item_DropCollectible
; Replaces:
;   or      a0, s6, r0
;   addiu   a1, sp, 0x5C
    jal     bg_haka_tubo_drop_params_hack
    or      a0, s6, r0

.org 0x8099c378 ; Hack call to Item_DropCollectible
; Replaces:
;   jal     Item_DropCollectible
    jal     BgHakaTubo_DropCollectible_Hack
