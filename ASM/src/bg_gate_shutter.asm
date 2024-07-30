; Check the new gate open flag instead of the master sword check
; This happens after the zelda's letter check so it should only effect it when the setting is set to open
; Put the flag into t9 because it will be checked against 0 when we return
; we can use t8
bg_gate_shutter_open_hack:
    li      t8, OPEN_KAKARIKO
    lb      t8, 0x00(t8) ; read the value of the OPEN_KAKARIKO setting. If we set it to 2 then it's always open
    jr      ra
    andi    t9, t8, 0x02
