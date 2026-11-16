.headersize (0x80AD1C20 - 0xE51A60)

; Control if Fado (blonde Kokiri girl) can spawn in Lost Woods
.org 0x80AD3A84    ; Fado branch at end of EnKo_CanSpawn (called by EnKo_Init), override to always true
    addiu   t5, $zero, 0x0031
.org 0x80AD3EB0    ; end of EnKo_Init, controls Fado spawn
    jal     check_fado_spawn_flags
    sw      t8, 0x0180(s0)
    lw      $ra, 0x001C($sp)
    lw      s0, 0x0018($sp)
    jr      $ra
    addiu   $sp, $sp, 0x0020

; Fix Fado's text id when trading in the odd potion out of order
.org 0x80AD37A4 ; vrom 0xE535E4
    sh      t2, 0x010E(s0)

.headersize 0
