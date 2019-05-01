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
    
    ;v0 is the TextID (from the hook!)
    
    la t1, Saria_Hints_Globals
    lw t2, 0x0000 (t1)      ;Load Last TextID
    
    ori t3, r0, 0x00e0  ; ID-You want to talk to Saria, right?
 beq t2, t3, @@Saria_TextID_StartNew
    nop
    
    ori t3, r0, 0x00e3  ; ID-Do you want to talk to Saria again?
 beq t2, t3, @@Saria_TextID_StartNew
    nop
    
    J @@Saria_TextID_Continue
    nop
    
@@Saria_TextID_StartNew:
    sw r0, 0x0004 (t1)          ;Reset Text Index
    
@@Saria_TextID_Continue:
    sw v0, 0x0000 (t1)          ;Save Last TextID
    
    
    lw t2, 0x0008 (t1)          ;Load Activation
 bne t2, r0, @@Saria_TextID_Change
    nop
           
    
; Is it a Saria Text?    
    
    ori t2, r0, (0x0160 -1)                  ;saria Text ID low
    slt t1, t2, v0        

 beq t1, r0, @@Saria_TextID_END      ;BRANCH if reqested Textpointer A1 < Min
    nop
    
    ori t2, r0, (0x016c +1)                  ;saria Text ID high - TBD is this correct? 
    slt t1, v0, t2   
    
  beq t1, r0, @@Saria_TextID_END      ;BRANCH if reqested Textpointer A1 < Min
    nop    
 
@@Saria_TextID_Change: 
    ori t2, r0, 0x0001
    la t1, Saria_Hints_Globals
    sw t2, 0x0008 (t1)          ;save Activation  
     
    la a0, Saria_Hints_Globals
    la a1, SARIA_GOSSIP_TEXTID_TABLE
    jal get_Next_Gossip_TextID  ; in __C__
    nop
    ; Modifying v0 with the new TextID


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
    
 bne t2, r0, @@SARIA_HINTS_GOSSIP_READING_NOSAVE ;if Saria Text Activation is active, no saving
    nop
    
    ; Get Message Text Index offset
    la a0, SARIA_GOSSIP_TEXTID_TABLE
    jal get_SariaIndexOffset_ByTextAddress ;in __C__
    nop
    ; v0 has the indexoffset now

    move a0, v0                     ;a1 is indexoffset of gossiptext now
    jal Saria_Gossip_Saveprogress       ;in __C__
    nop

@@SARIA_HINTS_GOSSIP_READING_NOSAVE:    

    ;Restore RA and return
    lw      ra, 0x0014(sp)
    addiu   sp, sp, 0x18
    jr ra
    nop    
    
    
    
    
    
    