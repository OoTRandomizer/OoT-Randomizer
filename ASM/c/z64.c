#include "z64.h"

/**
 * Symbol addresses from the original game
 *
 * `.global SYM_NAME` tells the assembler that the symbol should be global,
 * i.e. accessable from other files
 * 
 * `.equ SYM_NAME, 0xF00DFACE` sets the symbol `SYM_NAME` to have address
 * `0xF00DFACE`
 */

asm("\
.global z64_Inventory_ChangeUpgrade; \
    .equ z64_Inventory_ChangeUpgrade, 0x80081294; \
");

asm("\
.global gItemSlots; \
    .equ gItemSlots, 0x800F8F34; \
");

asm("\
.global gUpgradeCapacities; \
    .equ gUpgradeCapacities, 0x800F8CCC; \
");
