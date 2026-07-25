; Skull Kid Enemy Drop Override
; Hack at call to Item_DropCollectible to set drop_collectible_override_flag

en_skj_drop_collectible_hook:
    or      a0, s0, r0 ; Copy actor pointer to a0
    j     en_skj_drop_collectible_hack
    or      a1, s1, r0
