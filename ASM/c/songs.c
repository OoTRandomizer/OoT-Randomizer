#include "get_items.h"
#include "item_table.h"
#include "z64.h"

extern uint8_t MW_SEND_OWN_ITEMS;
extern uint8_t SONGS_AS_ITEMS;

void mw_send_own_songs() {
    if (MW_SEND_OWN_ITEMS && !SONGS_AS_ITEMS) {
        for (int i = 0; i < 12; i++) {
            if (z64_file.scene_flags[0x4A].unk_00_ & 1 << i) continue;
            override_key_t override_key = { .scene = 0xFF, .type = OVR_DELAYED, .flag = 0x20 + i };
            override_t override = lookup_override_by_key(override_key);
            item_row_t* item_row = get_item_row(override.value.base.item_id);
            int16_t quest_bit = item_row->effect_arg1;
            override.value.base.item_id - GI_SONG_MIN;
            if (z64_file.quest_items & 1 << quest_bit) {
                push_outgoing_override(&override);
                z64_file.scene_flags[0x4A].unk_00_ |= 1 << i;
            }
        }
    }
}
