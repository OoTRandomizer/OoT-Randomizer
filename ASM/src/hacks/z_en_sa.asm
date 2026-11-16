.headersize (0x80aa8bc0 - 0x00e28a10)

;li v1, 5
.orga 0xE29388          ; in func_80AF5DFC
    j   override_saria_song_check

; Set flag for player having received Saria's item
; Replaces  sw      s1,32(sp)
;           move    a2,a1
.org 0x80aa9f84         ; in func_80AF68E4
    jal     set_saria_song_flag
    sw      s1,32(sp)
