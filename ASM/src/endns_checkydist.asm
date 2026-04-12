; z_en_dns
EnDns_CheckYDist:
    move    a0,s0
    lui     at,0x42c8
    lwc1    $f0,148(s0)
    mtc1    at,$f4
    abs.s   $f0,$f0
    c.lt.s  $f0,$f4
    bc1fl   @@EnDns_OutsideRange
    nop                     ; in Y talking range, continue function
    jr      ra              ; 0x80a7550c
    nop
@@EnDns_OutsideRange:       ; outside of Y talking range, return function
    addi    ra,ra,0x8c
    jr      ra              ; 0x80a75598
    nop

