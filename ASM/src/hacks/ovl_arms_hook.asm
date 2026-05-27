.headersize (0x8090fb40 - 0x00cad2c0)

; Make D-pad down (0x400) interrupt firing Hookshot
; Replaces andi    t3,t2,0xc01f
.org 0x80910420         ; in ArmsHook_Shoot
    andi    t3,t2,0xc41f
