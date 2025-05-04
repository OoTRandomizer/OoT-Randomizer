; Hacks in player overlay

.headersize(0x808301C0 - 0xBCDB70)

; Hack in Player_PlayVoiceSfx so we can adjust volume
; Hack the call to Player_PlaySfx to call our own version
.org 0x808306A8
; Replaces:
;   jal     Player_PlaySfx
    jal     Player_PlaySfxWithVolume
