gohma_climb:
    sh      $zero, 0x0186(s0)  ;patienceTimer = 0

    ; Displaced code
    lui     a1, 0x40A0
    jr      ra
    lui     a2, 0x3F00
