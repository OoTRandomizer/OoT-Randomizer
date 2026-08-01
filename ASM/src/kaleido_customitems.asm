KaleidoScope_CheckAgeReqItemScreen:
    li      at,44
    beql    at,v1,@@Return
    li      v0,9            ; don't grey ITEM_SOLD_OUT menu item texture
    addu    v0,v1
    lbu     v0,(v0)         ; other items, return normal item age requirement
@@Return:
    jr      ra
    nop
