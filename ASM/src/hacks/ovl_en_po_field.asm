; Hyrule Field Poe Hacks

.headersize(0x80AF7D60 - 0x00E75040)

; this->collider.base.ocFlags1 = OC1_ON | OC1_TYPE_ALL; to allow the poe soul to trigger the collision with more than just Link
; original code: addiu   t4, $zero, 0x0009
.org 0x80AF8660
    addiu   t4, $zero, 0x0039

; Since we changed the collision flags, restrict interactions to only Link and Epona when Link is riding.
.org 0x80AF9BE0
    jal     big_poe_soul_collision
    or      a0, s0, $zero ; Displaced code
