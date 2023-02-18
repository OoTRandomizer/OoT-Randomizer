;==========================================================
; Branch Macros
;==========================================================

//allow branching to absolute file addresses

.macro b_a, addr
    b (org() + addr - orga())
.endmacro

.macro beqz_a, reg1, addr
    beqz    reg1, (org() + addr - orga())
.endmacro

.macro bnez_a, reg1, addr
    bnez    reg1, (org() + addr - orga())
.endmacro

.macro bne_a, reg1, reg2, addr
    bne     reg1, reg2, (org() + addr - orga())
.endmacro

.macro beq_a, reg1, reg2, addr
    beq     reg1, reg2, (org() + addr - orga())
.endmacro

.macro bnezl_a, reg1, addr
    bnezl   reg1, (org() + addr - orga())
.endmacro
