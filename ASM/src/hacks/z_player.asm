.headersize(0x808301c0 - 0xbcdb70)

;================================================================================
; Fixes magic getting locked if frozen/electrified during spell cast, i.e. traps
; Also ensures that Farore's Wind doesn't consume magic before actually working
;================================================================================
; Call magic reset upon getting frozen
; Replaces  li      a1,255
;           li      a2,10
.org 0x80835df0                 ; in func_80837C0C
    jal     PlayerFrozenElectrifiedMagicReset
    li      a2,10

; Call magic reset upon getting electrified
; Replaces  li      a1,255
;           li      a2,80
.org 0x80835e4c                 ; in func_80837C0C
    jal     PlayerFrozenElectrifiedMagicReset
    li      a2,80

; Remove the Farore check for normal consume magic, so that it can be done
; once the respawn data has been set and spell actually worked
; Replaces  bgtz    t3,8084e770
.org 0x8084e71c                 ; in Player_Action_CastMagicSpell
    b       0x8084e770
    ;lui    v0,0x8012 is a branch target

; Consume magic once respawn point has been set
; Replaces  sw      t4,3716(v0)
;           sw      t5,3720(v0)
.org 0x8084e824                 ; in Player_Action_CastMagicSpell
    jal     PlayerSetFaroreMagicState
    sw      t4,3716(v0)
