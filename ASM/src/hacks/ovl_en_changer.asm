.headersize(0x80AC3500 - 0x00E43340)

;Following 2 hacks, allows for both chests in each room to be opened separately.
;Skips part of Flags_SetTreasure(play, this->leftChestNum & 0x1F)

.org 0x80AC3A60
TCG_SHUFFLE_PATCH_1_START:
    nop             ;nop out jal to chest opening function func_80020624 (Flags_SetTreasure)
TCG_SHUFFLE_PATCH_1_END:

.org 0x80AC3AA8
TCG_SHUFFLE_PATCH_2_START:
    nop             ;nop out jal to chest opening function func_80020624 (Flags_SetTreasure)
TCG_SHUFFLE_PATCH_2_END:

;Following 4 hacks prevents the floating item above the unopened chest
;Namely prevents Actor_Spawn(&play->actorCtx, play, ACTOR_EN_EX_ITEM, xPos, yPos, zPos, 0, 0, 0)

.org 0x80AC3B5C
TCG_SHUFFLE_PATCH_3_START:
    nop            ;nop out jal to func_80025110 (Actor_Spawn)
TCG_SHUFFLE_PATCH_3_END:

.org 0x80AC3BB4
TCG_SHUFFLE_PATCH_4_START:
    nop            ;nop out jal to func_80025110 (Actor_Spawn)
TCG_SHUFFLE_PATCH_4_END:


.org 0x80AC3C04
TCG_SHUFFLE_PATCH_5_START:
    nop            ;nop out jal to func_80025110 (Actor_Spawn)
TCG_SHUFFLE_PATCH_5_END:

.org 0x80AC3C5C
TCG_SHUFFLE_PATCH_6_START:
    nop            ;nop out jal to func_80025110 (Actor_Spawn)
TCG_SHUFFLE_PATCH_6_END:

;Sets t9 to 0 so conditional always branches rather than running code to open unopened chests when running
;back through the rooms

.org 0x80AC3968
TCG_SHUFFLE_PATCH_7_START:
    or      t9, $zero, $zero
TCG_SHUFFLE_PATCH_7_END:
