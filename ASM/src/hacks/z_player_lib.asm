.headersize(0x800110a0 - 0x00a87000)

;================================================================================
; Remote Hookshot part 2/2. Make PostLimbDrawGameplay stop updating hook rotation
; earlier than OoT by changing check from IA to item model like Majora's Mask
;================================================================================
; Replaces  lb      v0,321(s0)
;           li      at,16
;           lui     a0,0x800f
;           beq     v0,at,8007be00
;           addiu   a0,a0,31828
;           li      at,17
;           bnel    v0,at,8007bed4
;           lb      t4,2130(s0)
.org 0x8007bde0                         ; in Player_PostLimbDrawGameplay
    lui     a0,0x800f
    addiu   a0,a0,31828
    la      t8,REMOTE_HOOKSHOT_ENABLED  ; Load setting
    jal     PlayerHookPostlimbCheck     ; Check setting and do appropriate Hookshot check
    lb      at,(t8)
    nop
    nop
