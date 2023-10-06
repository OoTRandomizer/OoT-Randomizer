#include "z64.h"

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
