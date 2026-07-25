; v1 contains our actorinit pointer
; globalCtx is in 0x005C(sp)
; Flags_GetClear function is at 0x80020640
; Not sure why but the original function occassionally stores v1 to 0x004C(sp). Dunno if we need to do this.
actor_spawn_clear_check_hook:
lw  a0, 0x005C(sp)
addiu   sp, sp, -0x30
sw  ra, 0x20(sp)
sw  s0, 0x28(sp)
lh  a2, CURR_ACTOR_SPAWN_INDEX
; Check if we were called from Actor_SpawnAsChild. Primarily for anubis. Might be important for others
; Get the return address of the actor_spawn function from the stack
lb  a3, actor_spawn_as_child_flag
beqz a3, @@notspawnaschild
nop
@@spawnaschild:
; We were called from Actor_SpawnAsChild. Load the parent address from 0xBC(sp)
lw  a3, actor_spawn_as_child_parent
b   @@callhack
nop
@@notspawnaschild:
or  a3, r0, r0
@@callhack:

jal actor_spawn_clear_check_hack
or  a1, r0, v1
; Check the return value of our hack. 1 means return null, 0 means continue spawning the actor
;
lw  s0, 0x28(sp)
lw  ra, 0x20(sp)
;li  a2, 0xFFFF
;sh  a2, CURR_ACTOR_SPAWN_INDEX
jr  ra
addiu   sp, sp, 0x30
