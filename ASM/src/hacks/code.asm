.headersize(0x800110A0 - 0xA87000)

; New Actor_Kill function
; Jump from the start of the original function
.org 0x80020eb4
    j   Actor_Kill_New
    nop

; Hack Actor_SpawnAsChild so we can set a flag that this is the function being called. Used during our clear check hack to get the parent.
.org 0x800253f0
; Replaces:
;   addiu   sp, sp, -0x30
;   sw      ra, 0x2c(sp)
j   Actor_SpawnAsChild_Hook
nop
Actor_SpawnAsChild_Continue_Jump_Point: