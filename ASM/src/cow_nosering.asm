; Replace the address of EnCow_OverrideLimbDraw in the call to SkelAnime_DrawFlexOpa in EnCow_OverrideLimbDraw

.headersize (0x80b77570 - 0x00EF2C90)

.org 0x80b78704
; Replaces:
;   jal EnCow_OverrideLimbDraw ; (original)
    j    EnCow_OverrideLimbDrawNew
    nop