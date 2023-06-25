#include "shop_actors.h"
#include "item_table.h"
#include "get_items.h"

// The shop table has hard-coded get item IDs, object IDs, and draw IDs.
// Ice traps are cloaked with fake object IDs and draw IDs.
// To make progressive items match the current progressive tier, these
// IDs must be updated on shop load and every time an item is purchased.

void lookup_shop_draw_id(z64_game_t* play, EnGirlA* shelfSlot, ShopItemEntry* itemEntry) {
    uint16_t item_id = shelfSlot->getItemId;
    // filter shop refills
    if (item_id) {
        // SOLD OUT is given a get item ID of 0x53 for the slot,
        // which conflicts with the Gerudo Mask override if it's
        // shuffled and the override in the Gerudo Mask slot happens
        // to be progressive. To prevent the mask shot from filling up
        // with longshots or golden gauntlets, check the currently loaded
        // object ID for OBJECT_GI_SOLDOUT (0x148) before attempting to change it.
        //
        // This doesn't use the itemEntry because that is null when purchasing
        // the item. It can't be easily looked up outside the EnOssan overlay
        // that I know of.
        if (z64_ObjectIsLoaded(&play->obj_ctxt, shelfSlot->objBankIndex)) {
            if (play->obj_ctxt.objects[shelfSlot->objBankIndex].id == 0x148) {
                if (itemEntry != NULL) {
                    shelfSlot->giDrawId = itemEntry->giDrawId;
                }
                return;
            }
        }

        override_t override = lookup_override(&shelfSlot->actor, z64_game.scene_index, item_id);
        if(override.key.all != 0) {
            uint16_t base_item_id = override.value.looks_like_item_id ?
                override.value.looks_like_item_id :
                override.value.base.item_id;
            override_t model_override = override;
            model_override.value.base.item_id = base_item_id;
            uint16_t resolved_item_id = resolve_upgrades(model_override);
            item_row_t *item_row = get_item_row(resolved_item_id);
            // object IDs were already set earlier, use as a fallback if the
            // new one isn't loaded.
            int8_t objIndex = z64_ObjectIndex(&play->obj_ctxt, item_row->object_id);
            if (resolved_item_id != base_item_id && objIndex >= 0 && z64_ObjectIsLoaded(&play->obj_ctxt, objIndex)) {
                shelfSlot->objBankIndex = objIndex;
                shelfSlot->actor.alloc_index = shelfSlot->objBankIndex;
                shelfSlot->giDrawId = item_row->graphic_id - 1;
            } else {
                // item doesn't upgrade, object isn't in the object context, or object isn't loaded
                if (itemEntry != NULL) {
                    shelfSlot->giDrawId = itemEntry->giDrawId;
                }
            }
        } else {
            // no override, load normal shop model draw ID
            if (itemEntry != NULL) {
                shelfSlot->giDrawId = itemEntry->giDrawId;
            }
        }
    }
}

void update_shop_shelves(EnOssan* this, z64_game_t* play) {
    int32_t i;
    for (i = 0; i < 8; i++) {
        if (this->shelfSlots[i] != NULL) {
            lookup_shop_draw_id(play, this->shelfSlots[i], NULL);
        }
    }
}
