; Hacks in ovl_Demo_Kankyo for Door of Time settings

.headersize(0x809307C0 - 0x00CCDF30)

.org 0x80930C3C
; Replaces
;   jal     CutsceneFlags_Get
    jal     DemoKankyo_CutsceneFlags_Get_Hook
