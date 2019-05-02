;Accept86 Saria hints repeat
;==================================================================================================
    
.definelabel Saria_Gossip_Save_Offset, 0xD4 + (58 * 0x1C) +0x10 

Saria_Hints_Globals:  .word  0x0, 0x0, 0x0, 0x0   ;1:last TextID loaded, 2:internal GossipText index
                                             ;3:Activation, 4: just deactivated


SARIA_GOSSIP_TEXTID_TABLE:
.area (42*2+8), 0      ;somehow its 42 Gossip TextIDs?, 8 Bytes as Space to code
.endarea



Saria_TextBoxBreak_HOOK:
    addiu   sp, sp, -0x24
    sw      ra, 0x0014(sp)
    sw      a1, 0x0018(sp)
    sw      a0, 0x001C(sp)
    sw      a2, 0x0020(sp)

    ;displaced code
    jal OOT_Navi_Saria_TextID_Generation
    nop
    
    lw t2, SARIA_HINTS_CONDITION
 beq t2, r0, @@Saria_TextID_END
    nop
    
    ;TextID Handling
    la a0, Saria_Hints_Globals
    move a1, v0                 ;TextID in a1
    la a2, SARIA_GOSSIP_TEXTID_TABLE
    jal Saria_TextBoxBreak_handling ; in ___C___ Modifying v0 with the new TextID
    nop
    
@@Saria_TextID_END:    
    ;Restore RA and return
    lw      ra, 0x0014(sp)
    lw      a1, 0x0018(sp)
    lw      a0, 0x001C(sp)
    lw      a2, 0x0020(sp)
    addiu   sp, sp, 0x24
    jr ra
    nop  




Saria_TextBoxBreak_Chaining_HOOK:       ;in a subfunction in the TextBoxBreak function
    la t1, Saria_Hints_Globals
    lw t2, 0x0008 (t1)      ;Load Activation
    
 beq t2, r0, @@Saria_TextBoxBreak_Chaining_NoChange
    nop
    ;overwrite V0 to chain TextBoxes
    ori v0, r0, 5

@@Saria_TextBoxBreak_Chaining_NoChange:
    ;displaced code
    jr ra
    nop



Saria_TextBoxBreak_Chaining2_HOOK:      ; On the JalR FunctionPointer settings

    ;displaced code
    lw a0, 0x0020 (SP)
    
    la t1, Saria_Hints_Globals
    
    lw t2, 0x000C (t1)      ;Load just deactivated
 bne t2, r0, @@Saria_TextBoxBreak_Chaining_JustDeactivated
    nop

    lw t2, 0x0008 (t1)      ;Load Activation
    
 bne t2, r0, @@Saria_TextBoxBreak_Chaining_NoChange
    nop
    
    ;displaced code
    sw t6, 0x0130 (t7)     ;if TextBoxChaining active for Saria, no resetting with t6

@@Saria_TextBoxBreak_Chaining_NoChange:
    ;displaced code
    j Saria_TextBoxBreak_Chaining2_HOOK_END
    nop

@@Saria_TextBoxBreak_Chaining_JustDeactivated:
    sw r0, 0x000C (t1)      ;reset just deactivated
    lui t6, 0x801E
    ori t6, t6, 0x0C2c
    sw t6, 0x0130 (t7)     ;if TextBoxChaining just deactivated, set function pointer to normal value

    j @@Saria_TextBoxBreak_Chaining_NoChange
    nop





SARIA_HINTS_GOSSIP_READING: ;arguments: a1 = ROMTextAddress, a2 = TextID (unused)
    addiu   sp, sp, -0x18
    sw      ra, 0x0014(sp)
    
    
    la t1, Saria_Hints_Globals
    lw t2, 0x0008 (t1)      ;Load Activation
    
 bne t2, r0, @@SARIA_HINTS_GOSSIP_READING_NOSAVE ;if Saria text activation is active, no saving
    nop
    
    ; Get Message Text Index offset
    la a0, SARIA_GOSSIP_TEXTID_TABLE
    jal get_SariaIndexOffset_ByTextAddress  ;in __C__ get index offset
    nop
    ; v0 has the indexoffset now

    move a0, v0                     ;a0 is indexoffset of gossiptext now
    jal Saria_Gossip_Saveprogress       ;in __C__ - saving progress
    nop

@@SARIA_HINTS_GOSSIP_READING_NOSAVE:    

    ;Restore RA and return
    lw      ra, 0x0014(sp)
    addiu   sp, sp, 0x18
    jr ra
    nop    
    