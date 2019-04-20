;Accept86 Saria hints repeat
;==================================================================================================


saria_hints_Button_Hook:

    ; displaced code
    LW T1, 0x0004 (T9)
    SLL T2, T1, 15
    
 BGEZ T2, @@saria_hints_Button_END
    nop
    ; dont change T2 or save and restore it, used after hook
    
    
@@saria_hints_Button_END:
    
    jr ra
    nop